
--declare a new composite-type. replacement for an 2d-array,which can't be extended dynamically by plpgsql
DROP TYPE IF EXISTS grouped_geom CASCADE;
CREATE TYPE grouped_geom AS (
  internal_group integer,
  osm_id integer,
  geom geometry
);

DROP TYPE IF EXISTS multigeom_osm CASCADE;
CREATE TYPE multigeom_osm AS (
    osm_ids integer[],
    geom geometry
);

-- this function has a memory_leak! use the plpgsql function instead
--CREATE OR REPLACE FUNCTION group_geoms (input_geometry geometry)
--RETURNS SETOF grouped_geom AS
--$$
--
--dump = plpy.prepare("SELECT g.geom AS geom FROM ST_Dump($1) AS g", ["geometry"])
--dumped_geoms = plpy.execute(dump, [input_geometry])
--
--geometries = [geom['geom'] for geom in dumped_geoms]
--grouped_geoms = []
--
--intersect = plpy.prepare("SELECT ST_Intersects($1, $2)", ["geometry", "geometry"])
--
--for tmp_g1 in geometries:
--    match = False
--    for geom_list in grouped_geoms:
--        if match:
--            break
--        for tmp_g2 in geom_list:
--            intersecting_geoms =  plpy.execute(intersect, [tmp_g1, tmp_g2])
--            if intersecting_geoms[0]['st_intersects']:
--                match = True
--                geom_list.append(tmp_g1)
--                break
--    if not match:
--        grouped_geoms.append([tmp_g1])
--
--for i, geom_list in enumerate(grouped_geoms):
--    for geom in geom_list:
--        yield [i, geom]
--
--$$
--LANGUAGE 'plpythonu';

CREATE OR REPLACE FUNCTION multiline_merge (input_geometry geometry, input_ids integer[])
RETURNS SETOF multigeom_osm AS
$$
DECLARE
    geom geometry;
    output multigeom_osm;
    ids integer[];
BEGIN
    FOR geom, ids IN SELECT ST_Collect(m.geom), array_agg(m.osm_id) from multiline_pgsql(input_geometry, input_ids) as m GROUP BY m.internal_group LOOP
        output := (ids, geom);
        RETURN NEXT output;
    END LOOP;    
RETURN;
END;
$$
LANGUAGE 'plpgsql';


CREATE OR REPLACE FUNCTION multiline_pgsql (input_geometry geometry, input_ids integer[])
RETURNS SETOF grouped_geom AS
$$
DECLARE
    match boolean;
    grouped_elements integer;
    match_by integer;
    dumped_elements integer := 0;
    change_other_groups boolean;
    old_groups_length integer;
    max_group integer := 0;
    tmp_geom geometry;
    dumped_geom geometry;
    output_geom grouped_geom;
    grouped grouped_geom[];
    tmp_id integer;
BEGIN
    --RAISE NOTICE 'input geometry %', ST_AsText(ST_Transform(input_geometry, 4326));
    FOR dumped_geom IN SELECT foo.geom FROM ST_Dump(input_geometry) AS foo LOOP
        grouped_elements := array_upper(grouped, 1);
        dumped_elements := dumped_elements + 1;
        match := FALSE;
        match_by := 0;
        change_other_groups := FALSE;
        DECLARE
        old_groups integer[];
        BEGIN
        --RAISE NOTICE '######################';
        --RAISE NOTICE 'elements % <> dumped_elements %', elements, dumped_elements;
        --RAISE NOTICE 'geometry %', ST_AsText(ST_Transform(dumped_geom, 4326));
        --RAISE NOTICE 'grouped %', grouped;
        IF grouped_elements > 0 THEN
            FOR i IN 1 .. grouped_elements LOOP
                --RAISE NOTICE 'grouped[i]= %, geom %', grouped[i].internal_group, i;
                IF ST_Intersects(dumped_geom,grouped[i].geom) THEN
                    --RAISE NOTICE 'intersection found!';
                    IF match THEN
                        tmp_geom := grouped[i].geom;
                        change_other_groups := TRUE;
                        old_groups := old_groups || grouped[i].internal_group;
                        --RAISE NOTICE 'changed linestring %, % -> group %', i, old_group, match_by;
                        tmp_id := grouped[i].osm_id;
                        grouped[i] := (match_by, tmp_id, tmp_geom);
                    ELSE
                        match := TRUE;
                        match_by := grouped[i].internal_group;
                        tmp_id := input_ids[dumped_elements];
                        grouped[grouped_elements+1] := (match_by, tmp_id, dumped_geom);                        
                        --RAISE NOTICE 'new matched % % -> %', match_by, dumped_geom, elements+1;
                    END IF;
                END IF;
            END LOOP;
            IF NOT match THEN
                max_group := max_group + 1;
                tmp_id := input_ids[dumped_elements];
                grouped[grouped_elements+1] := (max_group, tmp_id, dumped_geom);
                --RAISE NOTICE 'insert new group and geom';
            ELSE
                IF change_other_groups THEN
                    old_groups_length := array_upper(old_groups, 1);
                    FOR i IN 1 .. grouped_elements LOOP
                        FOR j IN 1..old_groups_length LOOP
                        IF old_groups[j] = grouped[i].internal_group THEN
                            --RAISE NOTICE 'changed old group, %, %', old_group, match_by;
                            tmp_geom := grouped[i].geom;
                            tmp_id := grouped[i].osm_id;
                            grouped[i] := (match_by, tmp_id, tmp_geom);
                        END IF;
                        END LOOP;
                    END LOOP;
                END IF;
            END IF;
        ELSE
            --RAISE NOTICE 'insert first element';
            max_group := max_group + 1;
            tmp_id := input_ids[dumped_elements];
            grouped[1] := (max_group, tmp_id, dumped_geom);
            --RAISE NOTICE 'linestring % -> group %', dumped_elements, 1;
        END IF;
        END;
    END LOOP;
    
    grouped_elements := array_upper(grouped, 1);
    FOR i IN 1 .. grouped_elements LOOP
        output_geom := grouped[i];
        RETURN NEXT output_geom;
    END LOOP;
    
    RETURN;
END;
$$
LANGUAGE 'plpgsql';