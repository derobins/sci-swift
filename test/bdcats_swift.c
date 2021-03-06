/****** Copyright Notice ***
 *
 * PIOK - Parallel I/O Kernels - VPIC-IO, VORPAL-IO, and GCRM-IO, Copyright
 * (c) 2015, The Regents of the University of California, through Lawrence
 * Berkeley National Laboratory (subject to receipt of any required
 * approvals from the U.S. Dept. of Energy).  All rights reserved.
 *
 * If you have questions about your rights to use or distribute this
 * software, please contact Berkeley Lab's Innovation & Partnerships Office
 * at  IPO@lbl.gov.
 *
 * NOTICE.  This Software was developed under funding from the U.S.
 * Department of Energy and the U.S. Government consequently retains
 * certain rights. As such, the U.S. Government has been granted for itself
 * and others acting on its behalf a paid-up, nonexclusive, irrevocable,
 * worldwide license in the Software to reproduce, distribute copies to the
 * public, prepare derivative works, and perform publicly and display
 * publicly, and to permit other to do so.
 *
 ****************************/

/**
 *
 * Email questions to SByna@lbl.gov
 * Scientific Data Management Research Group
 * Lawrence Berkeley National Laboratory
 *
*/

// Description: This is a simple benchmark based on VPIC's I/O interface
//		Each process reads a specified number of particles into 
//		a hdf5 output file using only HDF5 calls
// Author:	Suren Byna <SByna@lbl.gov>
//		Lawrence Berkeley National Laboratory, Berkeley, CA
// Created:	in 2011
// Modified:	01/06/2014 --> Removed all H5Part calls and using HDF5 calls
// 

#include <Python.h>
#include <numpy/arrayobject.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <assert.h>
#include "hdf5.h"
#include "../src/python_vol.h"
#define NPY_NO_DEPRECATED_API NPY_1_9_API_VERSION
#include <math.h>
#include "timer.h"
struct timeval start_time[3];
float elapse[3];

// HDF5 specific declerations
herr_t ierr;
hid_t file_id,dcpl_id, dset_id;
hid_t filespace, memspace;
hid_t fapl;
hid_t plist_id=H5P_DEFAULT;

// Variables and dimensions
long numparticles = 8388608;	// 8  meg particles per process
long long total_particles, offset;

float *x, *y, *z;
float *px, *py, *pz;
int *id1, *id2;
int x_dim = 64;
int y_dim = 64; 
int z_dim = 64;

// Uniform random number
inline double uniform_random_number() 
{
	return (((double)rand())/((double)(RAND_MAX)));
}

void print_data(int n)
{
	int i;
	for (i = 0; i < n; i++)
		printf("%f %f %f %d %d %f %f %f\n", x[i], y[i], z[i], id1[i], id2[i], px[i], py[i], pz[i]);
}

// Create HDF5 file and read data
void read_h5_data(int rank)
{
	// Note: printf statements are inserted basically 
	// to check the progress. Other than that they can be removed
	dset_id = H5Dopen2(file_id, "x", H5P_DEFAULT);
        printf("%s:%u\n",__func__,__LINE__);
        fflush(stdout);
        ierr = H5Dread(dset_id, H5T_NATIVE_FLOAT, memspace, filespace, plist_id, x);
        printf("%s:%u\n",__func__,__LINE__);
        fflush(stdout);
        H5Dclose(dset_id);
	//if (rank == 0) printf ("Read variable 1 \n");

	dset_id = H5Dopen2(file_id, "y", H5P_DEFAULT);
        ierr = H5Dread(dset_id, H5T_NATIVE_FLOAT, memspace, filespace, plist_id, y);
	//dset_id = H5Dcreate(file_id, "y", H5T_NATIVE_FLOAT, filespace, H5P_DEFAULT, dcpl_id, H5P_DEFAULT);
        //ierr = H5Dread(dset_id, H5T_NATIVE_FLOAT, memspace, filespace, fapl, y);
        H5Dclose(dset_id);
	//if (rank == 0) printf ("Read variable 2 \n");

	dset_id = H5Dopen2(file_id, "z", H5P_DEFAULT);
        ierr = H5Dread(dset_id, H5T_NATIVE_FLOAT, memspace, filespace, plist_id, z);
	//dset_id = H5Dcreate(file_id, "z", H5T_NATIVE_FLOAT, filespace, H5P_DEFAULT, dcpl_id, H5P_DEFAULT);
        //ierr = H5Dread(dset_id, H5T_NATIVE_FLOAT, memspace, filespace, fapl, z);
        H5Dclose(dset_id);
	//if (rank == 0) printf ("Read variable 3 \n");

	dset_id = H5Dopen2(file_id, "id1", H5P_DEFAULT);
        ierr = H5Dread(dset_id, H5T_NATIVE_INT, memspace, filespace, plist_id, id1);
	//dset_id = H5Dcreate(file_id, "id1", H5T_NATIVE_INT, filespace, H5P_DEFAULT, dcpl_id, H5P_DEFAULT);
        //ierr = H5Dread(dset_id, H5T_NATIVE_INT, memspace, filespace, fapl, id1);
        H5Dclose(dset_id);
	//if (rank == 0) printf ("Read variable 4 \n");

	dset_id = H5Dopen2(file_id, "id2", H5P_DEFAULT);
        ierr = H5Dread(dset_id, H5T_NATIVE_INT, memspace, filespace, plist_id, id2);
	//dset_id = H5Dcreate(file_id, "id2", H5T_NATIVE_INT, filespace, H5P_DEFAULT, dcpl_id, H5P_DEFAULT);
        //ierr = H5Dread(dset_id, H5T_NATIVE_INT, memspace, filespace, fapl, id2);
        H5Dclose(dset_id);
	//if (rank == 0) printf ("Read variable 5 \n");

	dset_id = H5Dopen2(file_id, "px", H5P_DEFAULT);
        ierr = H5Dread(dset_id, H5T_NATIVE_FLOAT, memspace, filespace, plist_id, px);
	//dset_id = H5Dcreate(file_id, "px", H5T_NATIVE_FLOAT, filespace, H5P_DEFAULT, dcpl_id, H5P_DEFAULT);
        //ierr = H5Dread(dset_id, H5T_NATIVE_FLOAT, memspace, filespace, fapl, px);
        H5Dclose(dset_id);
	//if (rank == 0) printf ("Read variable 6 \n");

	dset_id = H5Dopen2(file_id, "py", H5P_DEFAULT);
        ierr = H5Dread(dset_id, H5T_NATIVE_FLOAT, memspace, filespace, plist_id, py);
	//dset_id = H5Dcreate(file_id, "py", H5T_NATIVE_FLOAT, filespace, H5P_DEFAULT, dcpl_id, H5P_DEFAULT);
        //ierr = H5Dread(dset_id, H5T_NATIVE_FLOAT, memspace, filespace, fapl, py);
        H5Dclose(dset_id);
	//if (rank == 0) printf ("Read variable 7 \n");

	dset_id = H5Dopen2(file_id, "pz", H5P_DEFAULT);
        ierr = H5Dread(dset_id, H5T_NATIVE_FLOAT, memspace, filespace, plist_id, pz);
	//dset_id = H5Dcreate(file_id, "pz", H5T_NATIVE_FLOAT, filespace, H5P_DEFAULT, dcpl_id, H5P_DEFAULT);
        //ierr = H5Dread(dset_id, H5T_NATIVE_FLOAT, memspace, filespace, fapl, pz);
        H5Dclose(dset_id);
	//if (rank == 0) printf ("Read variable 8 \n");
	//printf("Rank %d:\n",rank);
	//print_data(10);
}

int main (int argc, char* argv[]) 
{
	
	MPI_Init(&argc,&argv);
	if(argc != 3)
        	printf("argc != 3 ./SWIFT_BDCATS file nparticles\n");
	int my_rank, num_procs;
	const char plugin_name[7]="python";
	MPI_Comm_rank (MPI_COMM_WORLD, &my_rank);
	MPI_Comm_size (MPI_COMM_WORLD, &num_procs);
	numparticles = (atol (argv[2]));	
        MPI_Info info  = MPI_INFO_NULL;
	if (my_rank == 0) {printf ("Number of paritcles: %ld \n", numparticles);}
        //if(my_rank==0&&numparticles<1024*1024*1024) printf("Number of particles is %d million\n",numparticles/1024/1024);
        //else if(my_rank==0&&numparticles>=1024*1024*1024)printf("Number of particles is %d billion\n",numparticles/1024/1024/1024);
	fflush(stdout);
	x=(float*)malloc(numparticles*sizeof(double));
	y=(float*)malloc(numparticles*sizeof(double));
	z=(float*)malloc(numparticles*sizeof(double));

	px=(float*)malloc(numparticles*sizeof(double));
	py=(float*)malloc(numparticles*sizeof(double));
	pz=(float*)malloc(numparticles*sizeof(double));

	id1=(int*)malloc(numparticles*sizeof(int));
	id2=(int*)malloc(numparticles*sizeof(int));

	/*if (my_rank == 0)
	{
		printf ("Finished initializeing particles \n");
	}
	*/
	MPI_Allreduce(&numparticles, &total_particles, 1, MPI_LONG_LONG, MPI_SUM, MPI_COMM_WORLD);
        MPI_Scan(&numparticles, &offset, 1, MPI_LONG_LONG, MPI_SUM, MPI_COMM_WORLD);	
	offset -= numparticles;
	hid_t acc_tpl;

	char *file_name = argv[1];
	MPI_Barrier (MPI_COMM_WORLD);
        timer_on (0);
	printf("start\n");
	fflush(stdout);
         
/*SWIFT VOL Related Code Change*/
        Py_Initialize();
	import_array();
        acc_tpl = H5Pcreate (H5P_FILE_ACCESS);
        H5Pset_fapl_swift(acc_tpl,plugin_name, MPI_COMM_WORLD, MPI_INFO_NULL);
	H5Pset_all_coll_metadata_ops(acc_tpl, true);
/*Rados VOL Related Code Change*/
	file_id = H5Fopen(file_name , H5F_ACC_RDONLY, acc_tpl);
	if(file_id < 0) {
		printf("Error with opening file!\n");
		fflush(stdout);
		goto done;
	}

	if (my_rank == 0)
	{
		printf ("Opened HDF5 file... \n");
	}
	filespace = H5Screate_simple(1, (hsize_t *) &total_particles, NULL);
        memspace =  H5Screate_simple(1, (hsize_t *) &numparticles, NULL);
        plist_id = H5Pcreate(H5P_DATASET_XFER);
        H5Pset_dxpl_mpio(plist_id, H5FD_MPIO_COLLECTIVE);
	//printf("total_particles: %lld\n", total_particles);
	//printf("my particles   : %ld\n", numparticles);

        //H5Pset_dxpl_mpio(fapl, H5FD_MPIO_COLLECTIVE);
        H5Sselect_hyperslab(filespace, H5S_SELECT_SET, (hsize_t *) &offset, NULL, (hsize_t *) &numparticles, NULL);
	MPI_Barrier (MPI_COMM_WORLD);
	timer_off (0);
	timer_on (1);
	//printf("Rank:%d started\n",my_rank);
	read_h5_data(my_rank);
	//printf("Rank:%d ended\n",my_rank);
  	MPI_Barrier (MPI_COMM_WORLD);
	timer_off (1);
	free(x); free(y); free(z);
	free(px); free(py); free(pz);
	free(id1);
	free(id2);
        printf("%s:%u\n",__func__,__LINE__);
        fflush(stdout);
	if (my_rank == 0)
	{
		printf ("\nI/O cost (sec):\n");
		timer_msg (1);
		printf ("Metadata cost (sec):\n");
		timer_msg (0);
		printf ("\n");
	}

	//H5Sclose(memspace);
        //H5Sclose(filespace);
        //H5Pclose(acc_tpl);
        //H5Fclose(file_id);
	if (my_rank == 0) printf ("After closing HDF5 file \n");
    	printf("%s:%u\n",__func__,__LINE__);
    	fflush(stdout);
error:
    H5E_BEGIN_TRY {
        H5Fclose(file_id);
        H5Pclose(acc_tpl);
    } H5E_END_TRY;

done:
	H5close();
	MPI_Finalize();

	return 0;
}
