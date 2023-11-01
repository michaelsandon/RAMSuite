## Example 1: Preparing data for survival analysis
Understanding failure distributions provides an advantageous approach to maintenance optimisation. It is also common for the operations division of an asset management company to have a Computerised Maintenance Management System (CMMS) which captures useful data for survival analysis in a central repository. This example demonstrates the process of utilising CMMS (SAP) data for survival analysis.

**Scenario**

* Jane Doe is reviewing the fleet performance for the transfer pumps at their site.
* Jane looks at transfer pump A and recognises that it has a construction type oof "SU45"
* Jane performs a construction type search and finds all fleet pumps with construction type "SU45". 20 pumps are returned. Jane recognises that these pumps are in all different types of service and that failure modes and distributions can be service dependent.
* Acccordingly, Jane decides to limit their search to pumps with *TRANSFER* in the equipment Title and *SU45* in the construction type field. The following results are returned

| Notification Date | Pump   | Notification Number | Desc                               | Work Order Number | WO Start Date | WO finish Date |
|-------------------|--------|---------------------|------------------------------------|-------------------|---------------|----------------|
| 1/1/2012          | Pump A | 1004789             | Pump vibration too high - cracking |          22083602 | 1/1/2012      | 1/2/2012       |
| 12/3/2014         | Pump A | 1004983             | Planned Pump Replacement           |          22153803 | 1/6/2014      | 12/6/2014      |
| 27/12/2015        | Pump A | 1005014             | Pump vibration high                |          22204413 | 31/12/2015    | 7/1/2016       |
| 3/7/2017          | Pump A | 1005114             | Pump casing leaking                |          22227200 | 4/7/2017      | 28/7/2017      |
| 7/10/2018         | Pump A | 1005168             | Pump Noisy                         |          22360454 | 7/10/2018     | 21/10/2018     |
| 1/12/2020         | Pump A | 1005297             | Planned Pump Replacement           |          22361062 | 1/2/2021      | 8/2/2021       |
| 14/08/2011        | Pump B | 1005334             | Pump Leaking from casing           |          22416976 | 16/08/2011    | 3/09/2011      |
| 10/1/2014         | Pump B | 1005368             | Planned pump replacement           |          22509473 | 1/2/2014      | 6/2/2014       |
| 6/2/2016          | Pump B | 1005389             | Planned pump replacement           |          22588499 | 20/2/2016     | 28/2/2016      |
| 1/6/2018          | Pump B | 1005414             | Pump casing cracked                |          22611923 | 1/6/2018      | 30/6/2018      |
| 2/5/2012          | Pump C | 1005426             | Pump Planned Replacement           |          22746034 | 7/5/2012      | 11/5/2012      |
| 7/6/2015          | Pump C | 1006456             | Pump seized                        |          22748262 | 10/6/2015     | 26/6/2015      |
| 15/4/2017         | Pump C | 1006675             | Pump Vibrating Excessively         |          22760553 | 16/4/2017     | 1/5/2017       |
| 23/3/2019         | Pump C | 1006897             | Pump Planned Replacement           |          22892061 | 25/3/2019     | 30/3/2019      |







## Example 2: Digging a litte deeper
separating valve body and actuator modes





## Example 3: Testing for mixed mode data
