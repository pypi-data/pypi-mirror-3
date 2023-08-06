Introduction
============

First of all we have a sqlite test.db
    >>> from pkg_resources import resource_filename
    >>> db_path = resource_filename('redturtle.sqlcontents', 'tests/lipsum.db')
    >>> from sqlalchemy import create_engine
    >>> connection_url = 'sqlite:///%s' % db_path
    >>> engine = create_engine(connection_url)

The table sqlcontents contains mock data
    >>> example_query = 'SELECT * from lipsum ORDER by ID'
    >>> results = engine.execute(example_query)
    >>> results.fetchone()
    (1, u'Lorem ipsum dolor sit amet...

We have a Plone site where we can add SQLFolder objects that are able to connect
to a DB. 
    >>> self.login('contributor')
    >>> data = {'title': "SQL Folder Object", 'connection_url': connection_url}
    >>> newid = portal.invokeFactory('SQLFolder', 'sqlfolder', **data)
    >>> sqlfolder = portal[newid]
    >>> self.assertEqual(sqlfolder.Title(), data['title'])

The accessor connection_url is write only:
    >>> self.assertRaises(AttributeError, getattr, sqlfolder, 'getConnecton_url')

The folder can be adapted to an engine that connects using the folder
connection_url 
    >>> from redturtle.sqlcontents.adapters.engine import ISQLFolderEngine
    >>> engine = ISQLFolderEngine(sqlfolder)
    >>> results = engine.execute(example_query)
    >>> results.fetchone()
    (1, u'Lorem ipsum dolor sit amet...
    
Inside the sqlfolder we can create SQLQuery objects.
    >>> column_names=[{'key': 'id', 'value': ''},
    ...               {'key': 'value', 'value': 'Text'},]
    >>> data = {'title': "SQL Query Object", 'query': example_query,
    ...         'column_names': column_names}
    >>> newid = sqlfolder.invokeFactory('SQLQuery', 'sqlquery', **data)
    >>> sqlquery = sqlfolder[newid]
    >>> self.assertEqual(sqlquery.Title(), data['title'])
    >>> self.assertEqual(sqlquery.getQuery(), example_query)
    >>> sqlquery.getColumn_names()
    ({'key': 'id', 'value': ''}, {'key': 'value', 'value': 'Text'})
  
We have a view called sqlquery_view to return results
    >>> view = sqlquery.restrictedTraverse('sqlquery_view')
    >>> html = view()

The view can translate columns in to the names defined in the column_names field
of the sqlquery object:
    >>> view.column_names
    ['', 'Text']


    
