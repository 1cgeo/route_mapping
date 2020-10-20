import psycopg2
from functools import wraps

def transaction(func):
    @wraps(func)
    def inner(*args, **kwargs):
        args = list(args[:])
        conn = args[0].getConnection()
        cursor = conn.cursor()
        args.insert(1, cursor)
        try:
            query = func(*args)
            conn.commit()
        except Exception as e:
            conn.rollback()
            print("{} error: {}".format(func.__name__, e))
        finally:
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
        try:
            query = func(*args)
        except Exception as e:
            print("{} error: {}".format(func.__name__, e))
        finally:
            cursor.close()
            return query
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
    def getNearestRoutingPoint(self, cursor, x, y, srid, edgeSchemaName, edgeTableName):
        cursor.execute(
            '''WITH targetpoint AS (
                SELECT ST_GeomFromText('POINT({x} {y})', {srid}) AS geom
            )
            SELECT 
                id,
                ST_LineLocatePoint(ST_Transform(geom, {srid}), (SELECT geom from targetpoint)) AS "position",
                ST_AsText(ST_LineInterpolatePoint(ST_Transform(geom, {srid}), ST_LineLocatePoint(ST_Transform(geom, {srid}), (SELECT geom from targetpoint)))) AS "line_point",
                ST_Transform(geom, {srid}) AS "line_wkt"
            FROM 
                {schema}.{table}
            ORDER BY 
                ST_Distance((SELECT geom from targetpoint), ST_LineInterpolatePoint(ST_Transform(geom, {srid}), ST_LineLocatePoint(ST_Transform(geom, {srid}), (SELECT geom from targetpoint)))) ASC
            LIMIT 1;'''.format(
                x=x,
                y=y,
                srid=srid,
                schema=edgeSchemaName,
                table=edgeTableName
            )
        )
        query = cursor.fetchall()[0]
        return (query[0], query[1],)

    @notransaction
    def getRoute(self,
            cursor,
            edgeSourceId,
            edgeSourcePos,
            edgeTargetId,
            edgeTargetPos,
            srid,
            edgeSchemaName,
            edgeTableName,
            restrictionSchemaName,
            restrictionTableName,
            sourcePoint,
            targetPoint
        ):
        cursor.execute(
            '''WITH sourcepoint AS (
                SELECT ST_GeomFromText('POINT({sourceX} {sourceY})', {srid}) AS "geom"
            ),
            targetpoint AS (
                SELECT ST_GeomFromText('POINT({targetX} {targetY})', {srid}) AS "geom"
            ),
            routeedges AS (
                SELECT
                    edge.id,
                    edge.name,
                    edge.velocity,
                    route.seq,
                    ST_Transform(edge.geom, {srid}) AS "geom"
                FROM (
                    SELECT
                        *
                    FROM 
                        pgr_trsp(
                            'SELECT 
                                id::INT4, 
                                source::INT4, 
                                target::INT4, 
                                cost::FLOAT8, 
                                reverse_cost::FLOAT8 
                            FROM 
                                {edgeSchema}.{edgeTable}', 
                            {edgeSourceId}, 
                            {edgeSourcePos}, 
                            {edgeTargetId}, 
                            {edgeTargetPos},
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
                        {edgeSchema}.{edgeTable}
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
                            {srid}
                        ), 
                        routeedges.geom
                    ) 
                    AND 
                    NOT ST_Touches(routelines.geom, routeedges.geom)
            )
            SELECT * FROM routesteps ORDER BY seq;'''.format(
                edgeSourceId=edgeSourceId,
                edgeSourcePos=edgeSourcePos,
                edgeTargetId=edgeTargetId,
                edgeTargetPos=edgeTargetPos,
                srid=srid,
                edgeSchema=edgeSchemaName,
                edgeTable=edgeTableName,
                restrictionSchema=restrictionSchemaName,
                restrictionTable=restrictionTableName,
                sourceX=sourcePoint[0],
                sourceY=sourcePoint[1],
                targetX=targetPoint[0],
                targetY=targetPoint[1]
            )
        )
        query = cursor.fetchall()
        return query

    @transaction
    def buildRouteStructure(self,
            cursor,
            routeSchemaName,
            routeTableName,
            edgeSchemaName,
            edgeTableName
        ):
        cursor.execute('''
                SELECT pgr_nodeNetwork('edgv.rotas', 1e-8, the_geom:='geom');
            '''.format(schema=routeSchemaName, table=routeTableName)
        )
        cursor.execute('''
            SELECT 
                pgr_createTopology('{schema}.{table}',1e-8, the_geom:='geom', clean := TRUE);
            '''.format(schema=edgeSchemaName, table=edgeTableName)
        )
        cursor.execute('''
            ALTER TABLE 
                {schema}.{table} 
            ADD COLUMN IF NOT EXISTS 
                distance FLOAT8;
            '''.format(schema=edgeSchemaName, table=edgeTableName)
        )
        cursor.execute('''
            UPDATE 
                {schema}.{table}
            SET 
                distance = ST_Length(ST_Transform(geom, 4674)::geography) / 1000;
            '''.format(schema=edgeSchemaName, table=edgeTableName)
        )
        cursor.execute('''
            ALTER TABLE 
                {schema}.{table} 
            ADD COLUMN IF NOT EXISTS 
                velocity INT4;
            '''.format(schema=edgeSchemaName, table=edgeTableName)
        )
        cursor.execute('''
            UPDATE {edgeSchema}.{edgeTable} SET velocity = 
                CASE
                    WHEN old.limitevelocidade IS NOT NULL 
                    THEN old.limitevelocidade
                    ELSE 60
                END
            FROM 
                {routeSchema}.{routeTable} as old
            WHERE 
                {edgeSchema}.{edgeTable}.old_id = old.id;
            '''.format(
                edgeSchema=edgeSchemaName, 
                edgeTable=edgeTableName,
                routeSchema=routeSchemaName, 
                routeTable=routeTableName
            )
        )
        cursor.execute('''
                ALTER TABLE {schema}.{table} ADD COLUMN IF NOT EXISTS time FLOAT8;
            '''.format(schema=edgeSchemaName, table=edgeTableName)
        )
        cursor.execute('''
            ALTER TABLE {schema}.{table} ADD COLUMN IF NOT EXISTS cost FLOAT8;
            '''.format(schema=edgeSchemaName, table=edgeTableName)
        )
        cursor.execute('''
            UPDATE {schema}.{table} SET cost = distance/velocity;
            '''.format(schema=edgeSchemaName, table=edgeTableName)
        )
        cursor.execute('''
            ALTER TABLE {schema}.{table} ADD COLUMN IF NOT EXISTS bidirecional boolean;
            '''.format(schema=edgeSchemaName, table=edgeTableName)
        )
        cursor.execute('''
                UPDATE 
                    {edgeSchema}.{edgeTable} AS noded
                SET 
                    bidirecional = trecho.bidirecional
                FROM 
                    {routeSchema}.{routeTable} AS trecho 
                WHERE 
                    noded.old_id = trecho.id;
            '''.format(
                edgeSchema=edgeSchemaName, 
                edgeTable=edgeTableName,
                routeSchema=routeSchemaName, 
                routeTable=routeTableName
            )
        )
        cursor.execute('''
            ALTER TABLE {schema}.{table} ADD COLUMN IF NOT EXISTS reverse_cost FLOAT8;
            '''.format(schema=edgeSchemaName, table=edgeTableName)
        )
        cursor.execute('''
            UPDATE 
                {schema}.{table} as noded
            SET 
                reverse_cost = 
                    CASE
                        WHEN noded.bidirecional = TRUE 
                        THEN noded.cost
                        ELSE -1
                    END
            '''.format(schema=edgeSchemaName, table=edgeTableName)
        )

        cursor.execute('''
            ALTER TABLE {schema}.{table} ADD COLUMN IF NOT EXISTS name FLOAT8;
            '''.format(schema=edgeSchemaName, table=edgeTableName)
        )
        cursor.execute('''
            UPDATE 
                {edgeSchema}.{edgeTable} AS noded
            SET 
                name = (SELECT nome FROM {routeSchema}.{routeTable} WHERE id = noded.old_id);
            '''.format(
                edgeSchema=edgeSchemaName, 
                edgeTable=edgeTableName,
                routeSchema=routeSchemaName, 
                routeTable=routeTableName
            )
        )
        return True