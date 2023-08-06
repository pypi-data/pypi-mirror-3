
CREATE OR REPLACE FUNCTION multiline_center(multiline geometry, centroid geometry)
RETURNS geometry AS
$$
DECLARE
    result geometry;
    line geometry;
    min_dist float;
    tmp_dist float;
    nearest_line geometry;
BEGIN
    FOR line IN SELECT foo.geom FROM ST_Dump(multiline) AS foo LOOP
        tmp_dist := ST_Distance(line, centroid);
        IF min_dist > tmp_dist OR min_dist is NULL THEN
            min_dist := tmp_dist;
            nearest_line := line;
        END IF;
    END LOOP;
    result := ST_line_interpolate_point(nearest_line, ST_line_locate_point(nearest_line, centroid));
    RETURN result;
END;
$$
LANGUAGE 'plpgsql';