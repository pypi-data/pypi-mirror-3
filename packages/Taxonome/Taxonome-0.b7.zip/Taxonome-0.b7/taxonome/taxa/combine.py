from .collection import TaxonSet

def combine_datasets(target_ds, background_ds, distrib_ds_name):
    """Combine several taxa datasets into one.
    
    Parameters:
        target_ds, background_ds :
          Each should be a sequence of 2-tuples, (name, taxonset). The name will be
          used as the key in the taxa's info. All taxa from any target dataset are
          included in the output, whereas information from background datasets is
          only copied to taxa in target datasets. There must be at least one target
          dataset, and at least one other (either target or background).
          
          Target datasets may be any iterable collection of taxa. Background datasets
          should be TaxonSets or similar.
        
        distrib_ds_name : str
          The name of the dataset from which distribution information should be
          taken, or 'all' to combine distribution info from all datasets.
    
    Returns: A :class:`TaxonSet`.
    """
    def _check_distrib_ds(dsname):
        return (dsname == distrib_ds_name) or (distrib_ds_name == 'all')

    output = TaxonSet()

    for dsname, ds in target_ds:
        is_distrib_ds = _check_distrib_ds(dsname)
        for tax in ds:
            if tax in output:
                t2 = output[tax.name]
                t2.info[dsname] = tax.info
                if is_distrib_ds:
                    t2.distribution.update(tax.distribution)
            else:
                tax.info = {dsname: tax.info}
                if not is_distrib_ds:
                    tax.distribution = set()
                output.add(tax)

    for dsname, ds in background_ds:
        is_distrib_ds = _check_distrib_ds(dsname)
        for tax in output:
            t2 = ds.get_by_accepted_name(tax.name)
            tax.info[dsname] = t2.info
            if is_distrib_ds:
                tax.distribution.update(t2.distribution)
    
    return output
