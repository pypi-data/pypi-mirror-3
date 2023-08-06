= raisin.page =

This packages contains the pages.ini file, defining the pages available for the
repoze.bfg server.

It also contains the templates for all pages in the templates folder:

    * box.pt
    
    * homepage.pt
    
    * statistics.pt 

And static resources used for rendering the pages:

    * static

        * base.css
        
        * favicon.ico
        
        * images/
        
        * systemsbiology-visualizations/

= The ini file =

This is an example of a project page definition in the pages.ini file:

    [project]
    title = Project
    path = 'project/:project_name/'
    renderer = raisin.page:templates/statistics.pt
    rows = row1, row2,
    cols = col1, col2,
    breadcrumbs = homepage,

        [[row1]]
        columns = project_about, project_meta,

        [[row2]]
        columns = experiments, experiments,
    
* path

    * The path is used by repoze.bfg to route to this page. 

* renderer

    * The renderer is the template rendering the page. 

* rows

    * The rows is a list of row identifiers
    
* cols

    * The cols is a list of volumn identifiers
    
* breadcrumbs

    * The breadcrumbs is a list of breadcrumbs to show on the page

* row1 and row2

    * The sections define what boxes appear on the individual rows


