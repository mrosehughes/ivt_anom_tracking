This repository contains utilities to catalog IVT in the CMIP6 dataset.
create_IVTslab.py   - Extracts "slab" from full CMIP6 IVT files. User provides lonigitude/latitude
                      of desired slab. Output written to netCDF.
find_events.py      - Finds all events for all CMIP6 slabs. Provide range of event strength (ptiles)
                      and event duration (persistences).
plot_eventStats.py  - Plots PDFs of all CMIP6 slabs.
plot_slabPDFs.py    - Plots event-statistics for all CMIP6 models.