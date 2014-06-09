PatentSearcher
==============

    >>> import us_patent as up
    >>> ps = up.PatentSearcher()
    >>> ps.read_patent_data(keyword='naver',n_pool=50,loud=True)
    
    >>> ps.export_results_pickle('naver.list',explain=True)
    >>> ps.import_results_pickle('naver.list')
    
    >>> ps.read_items(loud=True)
    
    >>> ps.results
  
zlib.decompress  / ps.results[0][0]:URL ps.results[0][1]:page
    
    >>> ps.patent_pages
    
ps.patent_pages[0][0]:title, ps.patent_pages[0][1]:URL


    >>> ppa = PatentPageAnalyzer()
    >>> soup = ppa.read_item_page(ps.patent_pages[0])
    >>> references = ppa.find_reference_table(soup)
    >>> info = ppa.find_info_table(soup)
    