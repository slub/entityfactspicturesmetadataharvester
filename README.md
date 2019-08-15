# entityfactspicturesmetadataharvester - EntityFacts pictures metadata harvester

entityfactspicturesmetadataharvester is a commandline command (Python3 program) that reads depiction information (images URLs) from given [EntityFacts](https://www.dnb.de/EN/Professionell/Metadatendienste/Datenbezug/Entity-Facts/entity-facts_node.html) sheets* (as line-delimited JSON records) and retrieves the ([Wikimedia Commons](https://commons.wikimedia.org/wiki/Main_Page) file) metadata of these pictures (as line-delimited JSON records).

*) EntityFacts are "fact sheets" on entities of the Integrated Authority File ([GND](https://www.dnb.de/EN/Professionell/Standardisierung/GND/gnd_node.html)), which is provided by German National Library ([DNB](https://www.dnb.de/EN/Home/home_node.html))

## Usage

It eats EntityFacts sheets as line-delimited JSON records from *stdin*.

It puts the (Wikimedia Commons file) metadata of each picture one by one as line-delimited JSON record to *stdout*.

```
entityfactspicturesmetadataharvester

optional arguments:
  -h, --help                           show this help message and exit
```

* example:
    ```
    example: entityfactspicturesmetadataharvester < [INPUT LINE-DELIMITED JSON FILE WITH ENTITYFACTS SHEETS] > [OUTPUT PICTURES METADATA LINE-DELIMITED JSON FILE]
    ```
## Run

* clone this git repo or just download the [entityfactspicturesmetadataharvester.py](entityfactspicturesmetadataharvester/entityfactspicturesmetadataharvester.py) file
* run ./entityfactspicturesmetadataharvester.py
* for a hackish way to use entityfactspicturesmetadataharvester system-wide, copy to /usr/local/bin

### Install system-wide via pip

```
sudo -H pip3 install --upgrade [ABSOLUTE PATH TO YOUR LOCAL GIT REPOSITORY OF ENTITYFACTSPICTURESMETADATAHARVESTER]
```
(which provides you ```entityfactspicturesmetadataharvester``` as a system-wide commandline command)

## See Also

* [entityfactssheetsharvester](https://github.com/slub/entityfactssheetsharvester) - a commandline command (Python3 program) that retrieves EntityFacts sheets from a given CSV with GND identifiers and returns them as line-delimited JSON records
* [entityfactspicturesharvester](https://github.com/slub/entityfactspicturesharvester) - a commandline command (Python3 program) that reads depiction information (images URLs) from given EntityFacts sheets (as line-delimited JSON records) and retrieves and stores the pictures and thumbnails contained in this information