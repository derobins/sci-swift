#include <Python.h>
#include <numpy/arrayobject.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <assert.h>
#include "hdf5.h"
#include "../src/python_vol.h"
#define NPY_NO_DEPRECATED_API NPY_1_9_API_VERSION

int main(int argc, char **argv) {
	const char plugin_name[7]="python";
    char file_name[100];
	hid_t file_id, acc_tpl, under_fapl, vol_id, vol_id2, int_id, attr, space;
	int i;
	if(argc!=2)//4 parameters: python_vol fname 
	{
       printf("./python_vol_HDF5_File_open filename\n");
	   printf("Example:\n./python_vol_HDF5_File_open rocket.h5 \n");
	   return 0;
    }
    else{
	   strcpy(file_name,argv[1]);
	}
	//Initialize Python and Numpy Routine
	Py_Initialize();
	import_array();

    printf("Start testing\n");

	//Test VOL Plugin Setup
	under_fapl = H5Pcreate (H5P_FILE_ACCESS);
	H5Pset_fapl_native(under_fapl);
	assert(H5VLis_registered("native") == 1);
	vol_id = H5VLregister (&H5VL_python_g);
	assert(vol_id > 0);
	assert(H5VLis_registered(plugin_name) == 1);
	vol_id2 = H5VLget_plugin_id(plugin_name);
	H5VLinitialize(vol_id2, H5P_DEFAULT);
	H5VLclose(vol_id2);
	native_plugin_id = H5VLget_plugin_id("native");
	assert(native_plugin_id > 0);
	acc_tpl = H5Pcreate (H5P_FILE_ACCESS);
	size_t prop_size=sizeof(int);
 	char pyplugin_name[5]="py";
	int prop_def_value=0;
	H5Pinsert2(acc_tpl, pyplugin_name, prop_size, &prop_def_value, NULL, NULL, NULL, NULL, NULL, NULL);
    H5Pset_vol(acc_tpl, vol_id, &under_fapl);

	//Test HDF5 File Open 
	file_id = H5Fopen(file_name, H5F_ACC_RDONLY,acc_tpl);

	//Test HDF5 File Close
	H5Fclose(file_id);
    Py_Finalize();
	printf("Testing Complete\n");
	return 0;
}



