import psycopg2
from psycopg2 import sql
from functools import wraps

def transaction(func):
    @wraps(func)
    def inner(*args, **kwargs):
        args = list(args[:])
        conn = args[0].getConnection()
        cursor = conn.cursor()
        args.insert(1, cursor)
        query = []
        try:
            query = func(*args, **kwargs)
            conn.commit()
        except Exception as e:
            conn.rollback()
            cursor.close()
            raise Exception("{} error: {}".format(func.__name__, e))
        cursor.close()
        return query
    return inner

def notransaction(func):
    @wraps(func)
    def inner(*args, **kwargs):
        args = list(args[:])
        conn = args[0].getConnection()
        cursor = conn.cursor()
        args.insert(1, cursor)
        query = []
        try:
            query = func(*args, **kwargs)
            return query
        except Exception as e:
            cursor.close()
            raise Exception("{} error: {}".format(func.__name__, e))
    return inner

class Postgres:
    
    def __init__(
            self,
            dbName, 
            dbHost, 
            dbPort, 
            dbUser, 
            dbPassword
        ):
        super(Postgres, self).__init__()
        self.connection = None
        self.setConnection(dbName, dbHost, dbPort, dbUser, dbPassword)
        
    def setConnection(self, dbName, dbHost, dbPort, dbUser, dbPassword):
        self.connection = psycopg2.connect(
            u"dbname='{0}' user='{1}' host='{2}' port='{3}' password='{4}'".format(
                dbName, dbUser, dbHost, dbPort, dbPassword
            )
        )

    def getConnection(self):
        return self.connection

    @notransaction
    def getNearestRoutingPoint(self, cursor, point, srid, schemaName):
        cursor.execute(
            sql.SQL(
                '''WITH targetpoint AS (
                    SELECT ST_GeomFromText('POINT(%(x)s %(y)s)', %(srid)s) AS geom
                )
                SELECT 
                    id,
                    ST_LineLocatePoint(ST_Transform(geom, %(srid)s), (SELECT geom from targetpoint)) AS "position",
                    ST_AsText(ST_LineInterpolatePoint(ST_Transform(geom, %(srid)s), ST_LineLocatePoint(ST_Transform(geom, %(srid)s), (SELECT geom from targetpoint)))) AS "line_point",
                    ST_Transform(geom, %(srid)s) AS "line_wkt"
                FROM (
                    SELECT 
                        *,
                        rgeom AS "geom"
                    FROM
                        {schema}.{table}
                )  AS rotas_noded      
                ORDER BY 
                    ST_Distance((SELECT geom from targetpoint), ST_LineInterpolatePoint(ST_Transform(geom, %(srid)s), ST_LineLocatePoint(ST_Transform(geom, %(srid)s), (SELECT geom from targetpoint)))) ASC
                LIMIT 1;'''
            ).format(
                schema=sql.Identifier(schemaName),
                table=sql.Identifier('rotas_noded')
            ),
            {
                'x': float(point[0]),
                'y': float(point[1]),
                'srid': srid
            }
        )
        query = cursor.fetchall()[0]
        return (query[0], query[1],)

    @notransaction
    def getRoute(self,
            cursor,
            sourcePointEdgeInfo,
            targetPointEdgeInfo,
            srid,
            routeSchemaName,
            restrictionSchemaName,
            restrictionTableName,
            sourcePoint,
            targetPoint,
            vehicle
        ):
        cursor.execute(
            sql.SQL('''WITH sourcepoint AS (
                SELECT ST_GeomFromText('POINT(%(sourceX)s %(sourceY)s)', %(srid)s) AS "geom"
            ),
            targetpoint AS (
                SELECT ST_GeomFromText('POINT(%(targetX)s %(targetY)s)', %(srid)s) AS "geom"
            ),
            routeedges AS (
                SELECT
                    edge.id,
                    edge.name,
                    edge.velocity,
                    route.seq,
                    ST_Transform(edge.rgeom, %(srid)s) AS "geom"
                FROM (
                    SELECT
                        *
                    FROM 
                        pgr_trsp(
                            %(edgeQuery)s, 
                            %(edgeSourceId)s, 
                            %(edgeSourcePos)s, 
                            %(edgeTargetId)s, 
                            %(edgeTargetPos)s,
                            TRUE,
                            TRUE, 
                            'SELECT 
                                10000::FLOAT8 AS to_cost, 
                                id_2::INT4 AS target_id, 
                                id_1::TEXT AS via_path 
                            FROM 
                                {restrictionSchema}.{restrictionTable}'
                        )
                    ORDER BY seq
                ) AS route
                LEFT JOIN (
                    SELECT 
                        *
                    FROM 
                        {routeSchemaName}.rotas_noded
                ) AS edge
                ON route.id2 = edge.id
            ),
            routeline AS (
                SELECT 
                    ST_LineSubstring(
                        geom,
                        CASE
                            WHEN 
                                ST_LineLocatePoint(geom, (SELECT geom from targetpoint)) < ST_LineLocatePoint(geom, (SELECT geom from sourcepoint)) 
                        THEN 
                            ST_LineLocatePoint(geom, (SELECT geom from targetpoint))
                        ELSE 
                            ST_LineLocatePoint(geom, (SELECT geom from sourcepoint))
                        END,
                        CASE
                            WHEN 
                                ST_LineLocatePoint(geom, (SELECT geom from targetpoint)) > ST_LineLocatePoint(geom, (SELECT geom from sourcepoint)) 
                        THEN 
                            ST_LineLocatePoint(geom, (SELECT geom from targetpoint))
                        ELSE 
                            ST_LineLocatePoint(geom, (SELECT geom from sourcepoint))
                        END
                    ) AS "geom"
                FROM (
                    SELECT
                        ST_LineMerge(
                            ST_Union(
                                geom
                            )
                        ) AS "geom"
                    FROM
                        routeedges
                ) AS line
            ),
            pointssplit AS (
                SELECT 
                ST_Collect(ST_Intersection(a.geom, b.geom)) AS "geom"
                FROM 
                    routeedges as a, 
                    routeedges as b
                WHERE
                    a.id != b.id
                    AND
                    ST_Touches(a.geom, b.geom)
            ),
            preroutelines AS (
                    SELECT
                        (ST_Dump(ST_Split(geom, (SELECT geom FROM pointssplit)))).geom AS "geom"
                    FROM
                        routeline
            ),
            routelines AS (
                    SELECT
                        *
                    FROM
                        preroutelines
                    UNION
                    SELECT
                        geom
                    FROM routeline
                    WHERE NOT EXISTS (
                            SELECT
                                *
                            FROM
                                preroutelines
                    )
            ),
            routesteps AS (
                SELECT 
                    ROW_NUMBER () OVER (ORDER BY routeedges.name) AS "id",
                    ((ST_Length(routelines.geom::geography)/1000) / routeedges.velocity) AS "hours",
                    ST_Length(routelines.geom::geography)/1000 AS "distance_km",
                    routeedges.name,
                    routeedges.velocity,
                    routeedges.seq,
                    ST_AsText(routelines.geom) AS "wkt"
                FROM routelines
                INNER JOIN routeedges
                ON 
                    ST_Intersects(
                        ST_Transform(
                            ST_Buffer(routelines.geom::geography, 2, 'endcap=square join=round')::geometry, 
                            %(srid)s
                        ), 
                        routeedges.geom
                    ) 
                    AND 
                    NOT ST_Touches(routelines.geom, routeedges.geom)
            )
            SELECT * FROM routesteps ORDER BY seq;''').format(
                routeSchemaName=sql.Identifier(routeSchemaName),
                restrictionSchema=sql.Identifier(restrictionSchemaName),
                restrictionTable=sql.Identifier(restrictionTableName)
            ),
            {
                'edgeSourceId': int(sourcePointEdgeInfo[0]),
                'edgeSourcePos': float(sourcePointEdgeInfo[1]),
                'edgeTargetId': int(targetPointEdgeInfo[0]),
                'edgeTargetPos': float(targetPointEdgeInfo[1]),
                'srid': int(srid),
                'sourceX': float(sourcePoint[0]),
                'sourceY': float(sourcePoint[1]),
                'targetX': float(targetPoint[0]),
                'targetY': float(targetPoint[1]),
                'edgeQuery': self.getEdgeQuery(routeSchemaName, *vehicle)
            }
        )
        query = cursor.fetchall()
        return query

    def getEdgeQuery(self, 
            routeSchemaName, 
            vehicleWidth, 
            vehicleHeght, 
            vehicleTonnage, 
            isLargeVehicle
        ):
        return '''
            SELECT 
                id::INT4, 
                source::INT4, 
                target::INT4, 
                cost::FLOAT8, 
                reverse_cost::FLOAT8 
            FROM 
                {routeSchemaName}.rotas_noded
            {where}
            '''.format(
                routeSchemaName=routeSchemaName,
                where=self.getWhereEdgeQuery(vehicleWidth, vehicleHeght, vehicleTonnage, isLargeVehicle)
            )

    def getWhereEdgeQuery(self, 
            vehicleWidth, 
            vehicleHeght, 
            vehicleTonnage, 
            isLargeVehicle
        ):
        conditional = [
            '(largura_maxima IS NULL OR largura_maxima > {0})'.format(vehicleWidth) if vehicleWidth else '',
            '(altura_maxima IS NULL OR altura_maxima > {0})'.format(vehicleHeght) if vehicleHeght else '',
            '(tonelagem_maxima IS NULL OR tonelagem_maxima > {0})'.format(vehicleTonnage) if vehicleTonnage else '',
            '(proibido_caminhao IS FALSE)' if isLargeVehicle else ''
        ]
        conditional = ' AND '.join(list(filter(lambda row: True if row else False, conditional)))
        return 'WHERE {}'.format(conditional) if conditional else ''

    @transaction
    def buildRouteStructure(self,
            cursor,
            routeSchemaName,
            routeTableName
        ):
        cursor.execute(
            sql.SQL(
                ''' DROP TABLE IF EXISTS {routeSchema}.{tmpRouteTable};
                DROP TABLE IF EXISTS {routeSchema}.{edgeTable};
                CREATE TABLE {routeSchema}.{tmpRouteTable} AS 
                SELECT 
                    *, 
                    ST_LineMerge(geom) AS "rgeom" 
                FROM 
                    {routeSchema}.{routeTable};
                SELECT pgr_nodeNetwork(%(nodeparameter)s, 1e-8, the_geom:='rgeom');
                SELECT pgr_createTopology(%(topoparameter)s,1e-8, the_geom:='rgeom', clean:=TRUE);
                ALTER TABLE 
                    {routeSchema}.{edgeTable}
                ADD COLUMN IF NOT EXISTS 
                    distance FLOAT8;
                UPDATE 
                    {routeSchema}.{edgeTable}
                SET 
                    distance = ST_Length(ST_Transform(rgeom, 4674)::geography) / 1000;
                ALTER TABLE 
                    {routeSchema}.{edgeTable}
                ADD COLUMN IF NOT EXISTS 
                    velocity INT4;
                UPDATE {routeSchema}.{edgeTable} SET velocity = 
                    CASE
                        WHEN old.limitevelocidade IS NOT NULL 
                        THEN old.limitevelocidade
                        ELSE 60
                    END
                FROM 
                    {routeSchema}.{routeTable} as old
                WHERE 
                    {routeSchema}.{edgeTable}.old_id = old.id;
                ALTER TABLE 
                    {routeSchema}.{edgeTable} 
                ADD COLUMN IF NOT EXISTS time FLOAT8;
                ALTER TABLE 
                    {routeSchema}.{edgeTable}
                ADD COLUMN IF NOT EXISTS cost FLOAT8;
                UPDATE {routeSchema}.{edgeTable} SET cost = distance/velocity;
                ALTER TABLE {routeSchema}.{edgeTable} ADD COLUMN IF NOT EXISTS bidirecional boolean;
                UPDATE 
                    {routeSchema}.{edgeTable} AS noded
                SET 
                    bidirecional = trecho.bidirecional
                FROM 
                    {routeSchema}.{tmpRouteTable} AS trecho 
                WHERE 
                    noded.old_id = trecho.id;
                ALTER TABLE {routeSchema}.{edgeTable} ADD COLUMN IF NOT EXISTS reverse_cost FLOAT8;
                UPDATE 
                    {routeSchema}.{edgeTable} as noded
                SET 
                    reverse_cost = 
                        CASE
                            WHEN noded.bidirecional = TRUE 
                            THEN noded.cost
                            ELSE -1
                        END;
                ALTER TABLE {routeSchema}.{edgeTable} ADD COLUMN IF NOT EXISTS name TEXT;
                UPDATE 
                    {routeSchema}.{edgeTable} AS noded
                SET 
                    name = (SELECT nome FROM {routeSchema}.{tmpRouteTable} WHERE id = noded.old_id);

                ALTER TABLE {routeSchema}.{edgeTable} ADD COLUMN IF NOT EXISTS largura_maxima FLOAT8;
                UPDATE 
                    {routeSchema}.{edgeTable} AS noded
                SET 
                    name = (SELECT largura_maxima FROM {routeSchema}.{tmpRouteTable} WHERE id = noded.old_id);

                ALTER TABLE {routeSchema}.{edgeTable} ADD COLUMN IF NOT EXISTS altura_maxima FLOAT8;
                UPDATE 
                    {routeSchema}.{edgeTable} AS noded
                SET 
                    name = (SELECT altura_maxima FROM {routeSchema}.{tmpRouteTable} WHERE id = noded.old_id);

                ALTER TABLE {routeSchema}.{edgeTable} ADD COLUMN IF NOT EXISTS tonelagem_maxima FLOAT8;
                UPDATE 
                    {routeSchema}.{edgeTable} AS noded
                SET 
                    name = (SELECT tonelagem_maxima FROM {routeSchema}.{tmpRouteTable} WHERE id = noded.old_id);

                ALTER TABLE {routeSchema}.{edgeTable} ADD COLUMN IF NOT EXISTS proibido_caminhao BOOLEAN;
                UPDATE 
                    {routeSchema}.{edgeTable} AS noded
                SET 
                    name = (SELECT proibido_caminhao FROM {routeSchema}.{tmpRouteTable} WHERE id = noded.old_id);
                ''').format(
                routeSchema=sql.Identifier(routeSchemaName),
                routeTable=sql.Identifier(routeTableName),
                tmpRouteTable=sql.Identifier('rotas'),
                edgeTable=sql.Identifier('rotas_noded'),
            ),{
                'nodeparameter': '{}.rotas'.format(routeSchemaName),
                'topoparameter': '{}.rotas_noded'.format(routeSchemaName)
            }
            
        )
        return True