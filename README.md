# RGB BIN2TIF

This script converts BIN files to GeoTIFF images.

Note that image height and width are hardcoded:

```
    img_height = int(meta['sensor_variable_metadata']['height left image [pixel]'])
    img_width = int(meta['sensor_variable_metadata']['width left image [pixel]'])
```

Also, a experimentally derived offset is applied:

```
    # TERRA-REF
    lon_shift = 0.000020308287

    # Drone
    lat_shift = 0.000018292 #0.000015258894
```

## Inputs

## Outputs

## Arguments and Flags
* **Positional Arguments:** 
    * **Raw BIN file to process:** 'bin' 
* **Required Arguments:**
    * **Metadata file associated with bin file:** '-m', '--metadata'                
    * **Z-axis offset:** '-z', '--zoffset'
* **Optional Arguments:**
       
## Adapting the Script
                                        
### Example
