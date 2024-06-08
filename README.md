# RGB BIN2TIF

This script converts BIN files to GeoTIFF images.

Please note that image height and width are collected from the provided metadata, including:

```
    img_height = int(meta['sensor_variable_metadata']['height left image [pixel]'])
    img_width = int(meta['sensor_variable_metadata']['width left image [pixel]'])
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
