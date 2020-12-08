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
    def getLayerContrainsCodes(self, cursor, layerName):
        cursor.execute(
            sql.SQL(
                """SELECT d.column_name, pg_get_constraintdef(c.oid)
                FROM
                (SELECT conname, oid FROM  pg_constraint) c
                INNER JOIN
                (
                    SELECT column_name, constraint_name
                    FROM information_schema.constraint_column_usage WHERE table_name = %(table)s
                ) d
                ON (c.conname = d.constraint_name AND not(d.column_name = 'id'));"""
            ),
            {
                'table': layerName
            }
        )
        query = cursor.fetchall()
        if not query:
            return {}
        result = {}
        for field, text in query:
            if not(field and text):
                return 
            codeList = []
            for code in " ".join(" ".join(text.split("(")).split(")")).split(" "):
                if not code.isnumeric():
                    continue
                codeList.append(code)
            result[field] = ",".join(codeList)
        return result

    @notransaction
    def getLayerDomains(self, cursor, layerName, layerSchema):
        cursor.execute(
            sql.SQL(
                """SELECT pg_get_constraintdef(c.oid) AS cdef
                FROM pg_constraint c
                JOIN pg_namespace n
                ON n.oid = c.connamespace
                WHERE contype IN ('f')
                AND n.nspname = %(schema)s
                AND (
                    conrelid::regclass::text IN (%(schemaAndTable)s)
                    or
                    conrelid::regclass::text IN (%(table)s)
                );
                """
            ),
            {
                'table': layerName,
                'schema': layerSchema,
                'schemaAndTable': '{0}.{1}'.format(layerSchema,layerName )
            }
        )
        query = cursor.fetchall()
        if not query:
            return {}
        return {
            item[0].split('(')[1].split(')')[0].replace(' ', '') :
            item[0].split('(')[1].split('.')[1]
            for item in query
        }

    @notransaction
    def getAttributeValueMap(self, cursor, layerName, layerSchema):        
        domains = self.getLayerDomains(layerName, layerSchema)
        fieldsValueMap = []        
        for fieldName in domains:
            contrains = self.getLayerContrainsCodes(layerName)
            cursor.execute(
                sql.SQL(
                    "SELECT code, code_name FROM {0}.{1} {2};".format(
                        'dominios', 
                        domains[fieldName], 
                        'WHERE code IN ({0})'.format(contrains[fieldName]) if fieldName in contrains else ''
                    )
                )
            )
            query = cursor.fetchall()
            if not query:
                continue
            fieldsValueMap.append({
                'attribute': fieldName,
                'valueMap': {v : k for k, v in dict(query).items()}
            })
        return fieldsValueMap

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
            vehicle
        ):
        cursor.execute(
            sql.SQL('''WITH routeedges AS (
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
                                edge2.id::INT4 AS target_id, 
                                edge1.id::TEXT AS via_path
                            FROM  
                                {restrictionSchema}.{restrictionTable} AS rest
                            INNER JOIN {routeSchemaName}.rotas_noded as edge1
                            ON rest.id_1 = edge1.old_id
                            LEFT JOIN {routeSchemaName}.rotas_noded as edge2
                            ON rest.id_2 = edge2.old_id'
                        )
                    ORDER BY seq
                ),
                route AS (
                    SELECT
                        rota_geom.*,
                        CASE
                            WHEN (SELECT max(seq) AS seq FROM routeedges) = 0 THEN
                                CASE
                                    WHEN %(edgeSourcePos)s > %(edgeTargetPos)s
                                    THEN ST_LineSubstring(ST_Transform(geom_linha, %(srid)s), %(edgeTargetPos)s, %(edgeSourcePos)s)
                                    ELSE ST_LineSubstring(ST_Transform(geom_linha, %(srid)s), %(edgeSourcePos)s, %(edgeTargetPos)s)
                                END
                            WHEN seq = 0 THEN
                                CASE
                                    WHEN ST_LineLocatePoint(ST_Transform(geom_linha, %(srid)s), geom_ponto_next) > %(edgeSourcePos)s
                                    THEN ST_LineSubstring(ST_Transform(geom_linha, %(srid)s), %(edgeSourcePos)s, 1)
                                    ELSE ST_LineSubstring(ST_Transform(geom_linha, %(srid)s), 0, %(edgeSourcePos)s)
                                END
                            WHEN seq = (SELECT max(seq) AS seq FROM routeedges) THEN
                                CASE
                                    WHEN ST_LineLocatePoint(ST_Transform(geom_linha, %(srid)s), geom_ponto) > %(edgeTargetPos)s
                                    THEN ST_LineSubstring(ST_Transform(geom_linha, %(srid)s), %(edgeTargetPos)s, 1)
                                    ELSE ST_LineSubstring(ST_Transform(geom_linha, %(srid)s), 0, %(edgeTargetPos)s)
                                END
                            ELSE ST_Transform(geom_linha, %(srid)s)
                        END
                        AS geom
                    FROM (
                        SELECT routeedges.*, rn.*, v.the_geom AS geom_ponto, rn.rgeom AS geom_linha, LEAD(v.the_geom,1) OVER(ORDER BY routeedges.seq) AS geom_ponto_next
                        FROM edgv.rotas_noded AS rn
                        INNER JOIN routeedges ON routeedges.id2 = rn.id
                        LEFT JOIN edgv.rotas_noded_vertices_pgr AS v ON routeedges.id1 = v.id
                    ) AS rota_geom
                )
                {outputQuery}'''
            ).format(
                routeSchemaName=sql.Identifier(routeSchemaName),
                restrictionSchema=sql.Identifier(restrictionSchemaName),
                restrictionTable=sql.Identifier(restrictionTableName),
                outputQuery=sql.SQL(self.getOutputRouteQuery(vehicle[-2], vehicle[-1]))
            ),
            {
                'edgeSourceId': int(sourcePointEdgeInfo[0]),
                'edgeSourcePos': float(sourcePointEdgeInfo[1]),
                'edgeTargetId': int(targetPointEdgeInfo[0]),
                'edgeTargetPos': float(targetPointEdgeInfo[1]),
                'srid': int(srid),
                'edgeQuery': self.getEdgeQuery(routeSchemaName, *vehicle)
            }
        )
        query = cursor.fetchall()
        return [{
            'seq': item[0],
            'hours': item[1],
            'distancekm': item[2],
            'name': item[3],
            'velocity': item[4],
            'initials': item[5],
            'covering': item[6],
            'tracks': item[7],
            'note': item[8],
            'wkt': item[9],
            'cost': item[10]   
        } for item in query]

    def getOutputRouteQuery(self, vehicleMaxSpeed, isLargeVehicle):
        return '''SELECT
            seq,
            ((ST_Length(geom::geography)/1000) / {velocity}) AS "hours",
            (ST_Length(geom::geography)/1000) AS distanciakm,
            nome,
            {velocity} AS velocity,
            sigla,
            revestimento,
            nrfaixas,
            observacao,
            ST_AsText(geom) AS "wkt",
            cost
        FROM route ORDER BY seq;
        '''.format(
            velocity=self.getVelocityExpression(vehicleMaxSpeed, isLargeVehicle)
        )

    def getVelocityExpression(self, vehicleMaxSpeed, isLargeVehicle):
        v = 'COALESCE(limitevelocidadeveiculospesados, limitevelocidade, 60)' if isLargeVehicle else 'COALESCE(limitevelocidade, 60)'
        return 'LEAST({0}, {1})'.format(v, vehicleMaxSpeed) if vehicleMaxSpeed else v

    def getEdgeQuery(self, 
            routeSchemaName, 
            vehicleWidth, 
            vehicleHeght, 
            vehicleTonnage,
            vehicleMaxSpeed,
            isLargeVehicle
        ):
        return '''
            SELECT 
                id::INT4, 
                source::INT4, 
                target::INT4, 
                (3.6 * distanciakm/{velocity}) AS cost, 
                (
                    CASE
                        WHEN bidirecional = TRUE 
                        THEN (3.6 * distanciakm/{velocity})
                        ELSE -1
                    END
                )::FLOAT8 AS reverse_cost
            FROM 
                {routeSchemaName}.rotas_noded
            {where}
            '''.format(
                velocity=self.getVelocityExpression(vehicleMaxSpeed, isLargeVehicle),
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
            '(larguramaxima IS NULL OR larguramaxima > {0})'.format(vehicleWidth) if vehicleWidth else '',
            '(alturamaxima IS NULL OR alturamaxima > {0})'.format(vehicleHeght) if vehicleHeght else '',
            '(tonelagemmaxima IS NULL OR tonelagemmaxima > {0})'.format(vehicleTonnage) if vehicleTonnage else '',
            '(proibidocaminhoes IS FALSE OR proibidocaminhoes IS NULL )' if isLargeVehicle else ''
        ]
        conditional = ' AND '.join(list(filter(lambda row: True if row else False, conditional)))
        return 'WHERE {}'.format(conditional) if conditional else ''

    @transaction
    def buildRouteStructure(self,
            cursor,
            srid,
            routeSchemaName,
            routeTableName
        ):
        cursor.execute(
            sql.SQL(
                '''
                CREATE EXTENSION IF NOT EXISTS pgrouting;
                DROP TABLE IF EXISTS {routeSchema}.{tmpRouteTable};
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
                    distanciakm FLOAT8;
                UPDATE 
                    {routeSchema}.{edgeTable}
                SET 
                    distanciakm = ST_Length(ST_Transform(rgeom, %(srid)s)::geography) / 1000;
                ALTER TABLE {routeSchema}.{edgeTable} 
                ADD COLUMN IF NOT EXISTS 
                    bidirecional boolean;
                UPDATE 
                    {routeSchema}.{edgeTable} AS noded
                SET 
                    bidirecional = trecho.bidirecional
                FROM 
                    {routeSchema}.{routeTable} AS trecho 
                WHERE 
                    noded.old_id = trecho.id;
                ALTER TABLE {routeSchema}.{edgeTable} 
                ADD COLUMN IF NOT EXISTS 
                    nome TEXT;
                UPDATE 
                    {routeSchema}.{edgeTable} AS noded
                SET 
                    nome = (SELECT nome FROM {routeSchema}.{routeTable} WHERE id = noded.old_id);
                
                ALTER TABLE {routeSchema}.{edgeTable} ADD COLUMN IF NOT EXISTS 
                    alturamaxima FLOAT8;
                UPDATE 
                    {routeSchema}.{edgeTable} AS noded
                SET 
                    alturamaxima = (SELECT alturamaxima FROM {routeSchema}.{routeTable} WHERE id = noded.old_id);

                ALTER TABLE {routeSchema}.{edgeTable} 
                ADD COLUMN IF NOT EXISTS 
                    larguramaxima FLOAT8;
                UPDATE 
                    {routeSchema}.{edgeTable} AS noded
                SET 
                    larguramaxima = (SELECT larguramaxima FROM {routeSchema}.{routeTable} WHERE id = noded.old_id);

                ALTER TABLE {routeSchema}.{edgeTable} 
                ADD COLUMN IF NOT EXISTS 
                    tonelagemmaxima FLOAT8;
                UPDATE 
                    {routeSchema}.{edgeTable} AS noded
                SET 
                    tonelagemmaxima = (SELECT tonelagemmaxima FROM {routeSchema}.{routeTable} WHERE id = noded.old_id);

                ALTER TABLE {routeSchema}.{edgeTable} 
                ADD COLUMN IF NOT EXISTS 
                    proibidocaminhoes BOOLEAN;
                UPDATE 
                    {routeSchema}.{edgeTable} AS noded
                SET 
                    proibidocaminhoes = (SELECT proibidocaminhoes FROM {routeSchema}.{routeTable} WHERE id = noded.old_id);

                ALTER TABLE {routeSchema}.{edgeTable} 
                ADD COLUMN IF NOT EXISTS 
                    limitevelocidade FLOAT8;
                UPDATE 
                    {routeSchema}.{edgeTable} AS noded
                SET 
                    limitevelocidade = (SELECT limitevelocidade::FLOAT8 FROM {routeSchema}.{routeTable} WHERE id = noded.old_id);

                ALTER TABLE {routeSchema}.{edgeTable} 
                ADD COLUMN IF NOT EXISTS 
                    limitevelocidadeveiculospesados FLOAT8;
                UPDATE 
                    {routeSchema}.{edgeTable} AS noded
                SET 
                    limitevelocidadeveiculospesados = (SELECT limitevelocidadeveiculospesados FROM {routeSchema}.{routeTable} WHERE id = noded.old_id);
                
                ALTER TABLE {routeSchema}.{edgeTable} 
                ADD COLUMN IF NOT EXISTS 
                    sigla TEXT;
                UPDATE 
                    {routeSchema}.{edgeTable} AS noded
                SET 
                    sigla = (SELECT sigla FROM {routeSchema}.{routeTable} WHERE id = noded.old_id);

                ALTER TABLE {routeSchema}.{edgeTable} 
                ADD COLUMN IF NOT EXISTS 
                    observacao TEXT;
                UPDATE 
                    {routeSchema}.{edgeTable} AS noded
                SET 
                    observacao = (SELECT observacao FROM {routeSchema}.{routeTable} WHERE id = noded.old_id);

                ALTER TABLE {routeSchema}.{edgeTable} 
                ADD COLUMN IF NOT EXISTS 
                    nrfaixas INTEGER;
                UPDATE 
                    {routeSchema}.{edgeTable} AS noded
                SET 
                    nrfaixas = (SELECT nrfaixas FROM {routeSchema}.{routeTable} WHERE id = noded.old_id);

                ALTER TABLE {routeSchema}.{edgeTable}
                ADD COLUMN IF NOT EXISTS 
                    revestimento SMALLINT;
                UPDATE 
                    {routeSchema}.{edgeTable} AS noded
                SET 
                    revestimento = (SELECT revestimento FROM {routeSchema}.{routeTable} WHERE id = noded.old_id);
                ''').format(
                routeSchema=sql.Identifier(routeSchemaName),
                routeTable=sql.Identifier(routeTableName),
                tmpRouteTable=sql.Identifier('rotas'),
                edgeTable=sql.Identifier('rotas_noded'),
            ),{
                'srid': int(srid),
                'nodeparameter': '{}.rotas'.format(routeSchemaName),
                'topoparameter': '{}.rotas_noded'.format(routeSchemaName)

            }
            
        )
        return True