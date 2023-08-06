# -*- coding=utf -*-
import cubes.browser
    
# FIXME: required functionality
# 
# * number of items in drill-down
# * dimension values
# * drill-down sorting
# * drill-down pagination
# * drill-down limits (such as top-10)
# * facts sorting
# * facts pagination
# * dimension values sorting
# * dimension values pagination
# * remainder
# * ratio - aggregate sum(current)/sum(total) 
# * derived measures (should be in builder)

class AttributeMapper(object):
    """docstring for AttributeMapper"""

    def __init__(self, cube, mappings = None, locale = None):
        """Attribute mapper for a cube - maps logical references to 
        physical references (tables and columns)
        
        Attributes:
        
        * `cube` - mapped cube
        * `mappings` – dictionary containing mappings
        * `simplify_dimension_references` – references for flat dimensions 
          (with one level and no details) will be just dimension names, no 
          attribute name. Might be useful when using single-table schema, for 
          example, with couple of one-column dimensions.
        * `dimension_table_prefix` – default prefix of dimension tables, if 
          default table name is used in physical reference construction
        
        Mappings
        ++++++++
        
        Mappings is a dictionary where keys are logical attribute references
        and values are table column references. The keys are mostly in the form:
        
        * ``attribute`` for measures and fact details
        * ``attribute.locale`` for localized fact details
        * ``dimension.attribute`` for dimension attributes
        * ``dimension.attribute.locale`` for localized dimension attributes
        
        The values might be specified as strings in the form ``table.column`` 
        or as two-element arrays: [`table`, `column`].
        """
        
        super(AttributeMapper, self).__init__()

        if cube == None:
            raise Exception("Cube for mapper should not be None.")

        self.cube = cube
        self.mappings = mappings
        self.locale = locale
        
        self.simplify_dimension_references = True
        self.dimension_table_prefix = None
    
        self.collect_attributes()

    def collect_attributes(self):
        """Collect all cube attributes and create a dictionary where keys are 
        logical references and values are `cubes.model.Attribute` objects.
        This method should be used after each cube or mappings change.
        """

        self.attributes = {}
        
        for attr in self.cube.measures:
            self.attributes[self.logical(None, attr)] = (None, attr)

        for attr in self.cube.details:
            self.attributes[self.logical(None, attr)] = (None, attr)

        for dim in self.cube.dimensions:
            for level in dim.levels:
                for attr in level.attributes:
                    ref = self.logical(dim, attr)
                    self.attributes[ref] = (dim, attr)

    def logical(self, dimension, attribute):
        """Returns logical reference as string for `attribute` in `dimension`. 
        If `dimension` is ``Null`` then fact table is assumed. The logical 
        reference might have following forms:


        * ``dimension.attribute`` - dimension attribute
        * ``attribute`` - fact measure or detail
        
        If `simplify_dimension_references` is ``True`` then references for flat 
        dimensios without details is ``dimension``
        """

        if dimension:
            if self.simplify_dimension_references and \
                               (dimension.is_flat and not dimension.has_details):
                reference = dimension.name
            else:
                reference = dimension.name + '.' + str(attribute)
        else:
            reference = str(attribute)
            
        return reference

    def split_logical(self, reference):
        """Returns tuple (`dimension`, `attribute`) from `logical_reference` string. Syntax
        of the string is: ``dimensions.attribute``."""
        
        split = reference.split(".")

        if len(split) > 1:
            dim_name = split[0]
            attr_name = ".".join(split[1:])
            return (dim_name, attr_name)
        else:
            return (None, reference)

    def split_physical(self, reference, default_table = None):
        """Returns tuple (`table`, `column`) from `reference` string. 
        Syntax of the string is: ``dimensions.attribute``. Note: this method 
        works currently the same as :meth:`split_logical`. If no table is 
        specified in reference and `default_table` is not ``None``, then 
        `default_table` will be used."""

        ref = self.split_logical_reference(reference)
        return (ref[0] or default_table, ref[1])
        
    def physical(self, dimension, attribute, locale = None):
        """Returns physical reference as tuple for `logical_reference`. 
        If there is no dimension in logical reference, then fact table is 
        assumed. The returned tuple has structure: (table, column).

        The algorithm to find physicl reference is as follows::
        
            IF localization is requested:
                IF is attribute is localizable:
                    IF requested locale is one of attribute locales
                        USE requested locale
                    ELSE
                        USE default attribute locale
                ELSE
                    do not localize

            IF mappings exist:
                GET string for logical reference
                IF locale:
                    append '.' and locale to the logical reference

                IF mapping value exists for localized logical reference
                    USE value as reference

            IF no mappings OR no mapping was found:
                column name is attribute name

                IF locale:
                    append '_' and locale to the column name

                IF dimension specified:
                    # Example: 'date.year' -> 'date.year'
                    table name is dimension name

                    IF there is dimension table prefix
                        use the prefix for table name

                ELSE (if no dimension is specified):
                    # Example: 'date' -> 'fact.date'
                    table name is fact table name
        """
        
        reference = None

        # Fix locale: if attribute is not localized, use none, if it is
        # localized, then use specified if exists otherwise use default
        # locale of the attribute (first one specified in the list)

        try:
            if attribute.locales:
                locale = locale if locale in attribute.locales \
                                    else attribute.locales[0]
            else:
                locale = None
        except:
            locale = None

        # Try to get mapping if exists

        if self.cube.mappings:
            logical = self.logical(dimension, attribute)

            # Append locale to the logical reference

            if locale:
                logical += "." + locale

            # TODO: should default to non-localized reference if no mapping 
            # was found?

            reference = self.cube.mappings.get(logical)

            # Split the reference
            if isinstance(reference, basestring):
                reference = self.split_physical(reference, self.cube.fact or self.cube.name)

        # No mappings exist or no mapping was found - we are going to create
        # default physical reference
        
        if not reference:

            column_name = str(attribute)

            if locale:
                column_name += "_" + locale
            
            if dimension and not (self.simplify_dimension_references \
                                   and (dimension.is_flat 
                                        and not dimension.has_details)):
                table_name = str(dimension)

                if self.dimension_table_prefix:
                    table_name = self.dimension_table_prefix + table_name
            else:
                table_name = self.cube.fact or self.cube.name

            reference = (table_name, column_name)

        return reference

# QueryAttribute = collections.namedtuple("QueryAttribute", "logical, physical, label")

class StarBrowser(object):
    """docstring for StarBrowser"""
    
    def __init__(self, cube, locale = None):
        """StarBrowser is a SQL-based AggregationBrowser implementation that 
        can aggregate star and snowflake schemas without need of having 
        explicit view or physical denormalized table.

        Attributes:
        
        * `cube` - browsed cube

        .. warning:
            
            Not fully implemented yet.

        **Limitations:**
        
        * only one locale can be used for browsing at a time
        * locale is implemented as denormalized: one column for each language

        """
        super(StarBrowser, self).__init__()

        if cube == None:
            raise Exception("Cube for browser should not be None.")
            
        self.cube = cube
        self.mapper = AttributeMapper(cube, cube.mappings, locale)
    
    def attribute(self, obj):
        """Make sure that obj is a cell attribute"""
        if isinstance(obj, cubes.Attribute):
            return obj
        elif isinstance(obj, basestring):
            attr = self.mapper.attributes[obj]
        else:
            raise KeyError("Unknown cube attribute %s" % obj)
            
    
    def aggregate(self, cell, measures = None, drilldown = None, details = False, **options):
        # 1. collect selections
        # 2. create conditions

        measures = measures or self.cube.measures or []
        
        measures = [self.attribute(m) for m in measures]
        selection = []

        # Collect measures (as Query attributes)

        for attr in measures:
            logical = self.mapper.logical(attr) # do I need that?
            phys = self.mapper.physical(dimension = None, attribute = attr)
            selection += QueryAttribute(logical, phys, str(attr))

        query = StarQuery(cube, mapper)
        query.selection = selection

        query.prepare()

        # drilldown has:
        # * key selection attributes
        # * group by keys
        # * detail selection attributes
        # 

class StarQuery(object):
    """docstring for StarQuery"""
    def __init__(self, cube, mapper, fact_name):
        super(StarQuery, self).__init__()
        self.cube = cube
        self.mapper = mapper
        self.selection = None
        
        # Required:
        self.fact_name = fact_name
        self.fact_table = ...
        
        # Table aliases
        self.tables = OrderedDict()
        self.tables[fact_name] = fact_table
        
    def prepare(self):
        pass

    def _collect_joins(self):
        """Collect joins and register joined tables. All tables used should be 
        collected in this function."""

        self.logger.info("collecting joins and registering tables...")

        self.expression = self.tables[self.fact_name]
        
        if not self.joins:
            self.logger.info("no joins")

        # FIXME: IMPORTANT: check whether we really need to do the join
        # Therefore:
        # * do not collect all cube joins
        # * get only joins that are necessary
        """Required joins?
        
        All attributes:
        * selection
        * slicing
        * grouping
        * ordering

        Selection: 
            aggregated measures -> should be in fact = no joins
            fact details -> only in non-aggregated queries
            dimension keys -> might be in fact or might join dimension detail table
            dimension details -> join dimension detail table
            
        Slicing: all point cuts + all range cuts + all set cuts
        Grouping: drill-downs (minus one level)
        Ordering: as details -> post-aggregation joins (???)
        
        * we are going to call everything in selection as details
          except aggrations
        * detail list should be explicitly mentioned
        * implicit details are:
            * drill-down dimension keys
            * drill-down dimension details, if requested - should be joined post-aggregation
        Q: is post join faster? 
        
        """
        
        for join in self.cube.joins:
            # self.logger.debug("joining detail '%s' to master '%s' %s")

            # Get master and detail table names and their respective keys that will be used for join
            master_name, master_key = self.mapper.split_physical(join["master"], self.fact_name)
            detail_name, detail_key = self.mapper.split_physical(join["detail"],)
            alias = join.get("alias")

            if not detail_name or detail_name == self.fact_name:
                raise ValueError("Detail table name should be present and should not be a fact table")

            master_table = self.table(master_name)
            detail_table = self.register_table(detail_name, alias = alias, schema = self.schema)

            try:
                master_column = master_table.c[master_key]
            except:
                raise Exception('Unable to find master key "%s"."%s" ' % (master_name, master_key))
            try:
                detail_column = detail_table.c[detail_key]
            except:
                raise Exception('Unable to find master key "%s"."%s" ' % (detail_name, detail_key))

            onclause = master_column == detail_column

            self.expression = expression.join(self.expression, detail_table, onclause = onclause)
        
    # def normalize_drilldown(self, drilldown):
    #     """Normalize a drilldown object. The `drilldown` might be a list or a 
    #     dictionary. If the `drilldown` is a list, then each item is a dimension 
    #     (or dimension name). Result is a dictionary where keys are dimension names
    #     and values are drill down level names.
    #     """
    #     result = OrderedDict()
    # 
    #     if type(drilldown) == list or type(drilldown) == tuple:
    #         self.logger.debug("converting drill-down specification to a dictionary")
    # 
    #         for dim in drilldown:
    #             dim = self.cube.dimension(dim)
    #             next_level = self._next_drilldown_level(dim) # FIXME
    #             result[dim.name] = next_level
    # 
    #     elif isinstance(self.drilldown, dict):
    #         self.logger.debug("updating next levels in drill-down dictionary")
    # 
    #         for dim, level in drilldown.items():
    #             dim = self.cube.dimension(dim)
    #             if level:
    #                 result[dim.name] = level
    #             else:
    #                 next_level = self._next_drilldown_level(dim)
    #                 result[dim.name] = next_level
    #     else:
    #         raise TypeError("Drilldown is of unknown type: %s" % drilldown.__class__)
    # 
    # def _next_drilldown_level(self, dim):
    #     """Get next drilldown level for dimension. If we are already cutting the dimension, then return
    #     next level to the last cut level. If we are not cutting, return first level.
    #     
    #     Dimension should already by a dimension object, not a string.
    #     """
    #     
    #     # FIXME: only default hierarchy is currently used
    #     
    #     last_level = self._last_levels.get(dim.name)
    #     if last_level:
    #         next_level = dim.default_hierarchy.next_level(self._last_levels[dim.name])
    #         if not next_level:
    #             raise ValueError("Unable to drill-down after level '%s'. It is last level "
    #                              "in default hierarchy in dimension '%s'" % 
    #                              (last_level.name, dim.name))
    #     else:
    #         next_level = dim.default_hierarchy.levels[0]
    # 
    #     return next_level
