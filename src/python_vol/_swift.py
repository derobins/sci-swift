#HDF5 Swift VOL in Python
#Mar 18 2018
#Jialin Liu
#LBNL/NERSC
#How we start a new python vol?
#First, copy the template _h5py.py
#import h5py
import numpy
from __swift_file import swift_container_create
from __swift_file import swift_container_open
from __swift_dataset import swift_object_create
from __swift_dataset import swift_object_open
from __swift_dataset import swift_metadata_create
from __swift_dataset import swift_metadata_get
from __swift_dataset import swift_object_download
class H5PVol:
	dt_types={ 0:"int16", 1:"int32",2:"float32",3:"float64"}
	obj_curid = 1   # PyLong_AsVoidPtr can not convert 0 correctly
	obj_list  = {}
	'''
	dictionary for various h5py objects, e.g., groups, datasets, links, etc.
	starting obj is reserved for HDF5 file handle, with index 0 as its key
	{0:hdf5_handle, ...}
	'''
	def H5VL_python_file_create(self, name, flags, fcpl_id, fapl_id, dxpl_id, req, ipvol):
		#print ("------- PYTHON H5Fcreate:%s"%name)
		#print ("------- PYTHON Vol: %d"%ipvol)
		if(ipvol==0):
			try:
				self.obj_curid=1
				self.obj_list={} #reset
				swift_container_create(name) # create a container for this file, container name = file name
				#save container_name in the runtime dictionary, at user level, code can get back container by the returned id, 	
				self.obj_list[self.obj_curid]=name
				curid=self.obj_curid
				self.obj_curid=curid+1
				return curid
			except Exception as e:
				print ('file create failed in python with error: ',e)
				return -1
		else:
			print ("%d py vol is not implemented"%ipvol)
			return -1

	def H5VL_python_file_open(self, name, flags, fapl_id, dxpl_id, req, ipvol):
		#print ("------- PYTHON H5Fopen:%s"%name)
	        #print ("------- PYTHON Vol: %d"%ipvol)
		if(ipvol==0):
			try:
				self.obj_curid=1 #reset
				self.obj_list={} #reset
				#Probably just check if (metadata, container validation, file)
				# save file name--> container name in the runtime dictionary. 
				# at user level, dataset api, etc, can get back container name for read/write (get/put) 
				container_name = name
				container_id = swift_container_open(container_name)
				if container_id ==1: # file exists
					self.obj_list[self.obj_curid]=container_name
					curid=self.obj_curid
					self.obj_curid=curid+1
					return curid
				else:
					print("returned -1 in python file open")
					return -1
			except Exception as e:
				print ('file create failed in python with error: ',e)
				return -1
		else:
			print ("%d py vol is not implemented"%ipvol)
			return -1

	def H5VL_python_dataset_open(self, obj_id, loc_params, name, dapl_id, dxpl_id, req):
		#print ("------- PYTHON H5Dopen:%s"%name)
		try:
			container_name=self.obj_list[obj_id] #retrieve container name based on obj_id
			#print ('in dt open, container is:%s,object name:%s'%(container_name,name))
			#reconstruct full path
			full_path=container_name+"/"+name
			z=full_path.replace("/","\\")
			container_name = z[:z.find(z.split('\\')[-1])-1]
                        obj_name = z.split('\\')[-1]
			#print('full_path:%s'%full_path)
			#print('container name:%s'%container_name)
			#print('obj name:%s'%obj_name)
			metadata = swift_metadata_get(container=container_name,sciobj_name=obj_name)
			#print("In dataset open")
			#print (metadata)
			#print ("end showing metadata")
			curid = self.obj_curid
			self.obj_list[curid] = full_path
			self.obj_curid = curid+1
			return curid
			#try:
			#	metadata = swift_metadata_get(container=container_name,sciobj_name=name)
			#	curid = self.obj_curid
				
			#	if(swift_object_open(container = container_name, sciobj_name=name)==1):
					#object exists
			#		curid = self.obj_curid
			#		dset_obj={'name':name,'shape':(1,),'dtype':'float'} #TODO: retrieve from swift store (name,shape,type )
			#		self.obj_list[curid] = dset_obj # insert object name 
			#		self.obj_curid = curid+1       # update current index
					# #print ("------- PYTHON H5Dopen OK")
					#print ('dataset id is %d'%curid)
			#		return curid
			#	else:
			#		print("dset obj not exists in container:%s"%container_name)
			#		return -1
			#except Exception as e:
			#	print ('dataset open in python failed with error: ',e)
			#	return -1
		except Exception as e:
			print ('retrieve obj failed in python dataset open:',e)
			return -1

	def H5VL_python_file_close(self, file_id, dxpl_id, req):
		try:
			if(len(self.obj_list)==0):
				#print ("------- PYTHON H5Fclose OK")
				return 1
			file_obj = self.obj_list[file_id] # retrive the file handle/obj based on id 'file_id'
			if file_obj == None:
				#print ("Python File Obj is none")
				return 1
			else:
				#file_obj.close()
				self.obj_list={} # empty all ojects
				self.obj_curid=1 # reset index to 0, (1 for now, due to bug of PyLong_AsVoidPtr can not take 0)
				#print ("------- PYTHON H5Fclose OK")
				return 1
		except Exception as e:
			print ('file close failed in python with error:',e)
			return -1

	def H5VL_python_dataset_close(self, dset_id, dxpl_id, req):
		try:
			if (len(self.obj_list)==0):
				#print ("------- PYTHON H5Dclose OK")
				return 1
			dset_obj = self.obj_list[dset_id] # retrive the file handle/obj based on id 'dataset_id'
			if dset_obj == None:
				print ("Python Dataset Obj is none")
				return 1
			else:
				#dset_obj.close()
				del(self.obj_list[dset_id])
				#print ("------- PYTHON H5Dclose OK")
				return 1
		except Exception as e:
			print ('dataset close failed in python with error:',e)
			return -1

	def H5VL_python_group_create (self, obj_id, loc_params, name, gcpl_id, gapl_id, dxpl_id, req):
		#print ("------- PYTHON H5Gcreate:%s"%name)
		'''
		HDF5 Group is mapped to a container in swift
		The path to group is preserved as the container name
		Parent group will create a object to track this sub_group
		Example: create group '/coadd', (which is a subgroup under root group in HDF5)
			 Step 1: swift will create a container named 'filename.h5/coadd', 
			 Step 2: swift will also create a object named 'filename.h5/coadd' in the parent group (i.e., 'parent' container)
		'''
		try:
			#print ('in python group create, obj is ',obj_id)
			grp_parent_obj=self.obj_list[obj_id] # now the grp_parent_obj is the parent container's name
			try:
				#grp_obj=grp_parent_obj.create_group(name)
				new_container_name = grp_parent_obj+'\\'+name
				#print ("new container name:%s"%new_container_name)
				swift_container_create(new_container_name)
				curid = self.obj_curid
				self.obj_list[curid] = new_container_name # insert new object
				#print('in group create, obj id:%d, name:%s'%(curid,new_container_name))
				#create an empty object with name = name
				empty_sciobj_name = new_container_name
				#put this object into parent container for tracking purpose. 
				swift_object_create(container = grp_parent_obj,sciobj_name = empty_sciobj_name)
				self.obj_list[curid+1] = grp_parent_obj+'\\'+empty_sciobj_name
				self.obj_curid = curid+2	# update current head, points to future object			
				# #print ("------- PYTHON H5Gcreate OK")
				return curid # return new obj's id
			except Exception as e:
				print ('group create in python failed with error:',e)
				return -1
		except Exception as e:
			print ('retrieve obj failed in python group create')
			return -1

	def H5VL_python_dataset_create(self, obj_id, loc_params, name, dcpl_id, dapl_id, dxpl_id, req, ndims,pytype,dims,maxdims):
		#print ("------- PYTHON H5Dcreate:%s"%name)
		print ("-----------------ENTER Dataset Create-----------------")
		try:
			dst_parent_obj=self.obj_list[obj_id]
			name=name.replace("/","\\")
			z=dst_parent_obj+'\\'+name
			#print ('in dset create, full path is:%s,ndims:%d'%(z,ndims))
			dst_container_name = z[:z.find(z.split('\\')[-1])-1]
			dst_obj_name = z.split('\\')[-1]
			#print ('in dset create, obj id is %d, name:%s'%(obj_id,dst_parent_obj))
			try:
				#dst_obj=dst_parent_obj.create_dataset(name,dims,dtype=self.dt_types[pytype])
				sci_obj_source = numpy.empty(dims, dtype=self.dt_types[pytype], order='C')
				#print ('in dset create, contianer_name:%s,obj name:%s'%(dst_container_name,dst_obj_name))
				#print ("obj source: ",sci_obj_source)
				swift_object_create(container = dst_container_name, sciobj_name = dst_obj_name, sciobj_source = sci_obj_source)
				sci_obj_meta={}
				sci_obj_meta['type'] = str(self.dt_types[pytype])
				sci_obj_meta['dims'] = numpy.array_str(dims)
				sci_obj_meta['ndim'] = str(ndims)
				#print ('sci obj meta:',sci_obj_meta) 
				r1=swift_metadata_create(container = dst_container_name, sciobj_name = dst_obj_name, sciobj_metadata=sci_obj_meta)#TODO: append shape, type info into object's metadata
				#print("in dataset create, r1:",r1)
				curid = self.obj_curid
				self.obj_list[curid] = z # insert new object#TODO: need full name or not? April Fool Day Puzzle
				self.obj_curid = curid+1       # update current index
				#print ("------- PYTHON H5Dcreate OK")
				#print ('dataset id is %d'%curid)
				print ("-----------------LEAVE Dataset Create-----------------")
				return curid
			except Exception as e:
				print ('dataset create in python failed with error: ',e)
				return -1
		except Exception as e:
			print ('retrieve obj failed in python dataset create:',e)
			return -1

	def H5VL_python_dt_info(self, obj_id):
		try:
			#print ('query dt info: object name is:%s'%self.obj_list[obj_id])
			z=self.obj_list[obj_id]
			z=z.replace("/","\\")
			obj_name = z.split("\\")[-1]
			container_name = z[:z.find(z.split('\\')[-1])-1]
			#print("start query")
			#print ("container:%s"%container_name)
			#print ("object:%s"%obj_name)
			metadata = swift_metadata_get(container=container_name,sciobj_name=obj_name)
			#print("end query")
			#print (metadata)
			m=metadata['dims']
			m=m[1:len(m)-1]
			dims=numpy.fromstring(m,dtype=int,sep=' ')
			ndims=int(metadata['ndim'])
			#dims=self.obj_list[obj_id].shape
			#ndims=len(dims)
			#print ('ndims:%d'%ndims)
			#print ('dtype:',metadata['type'])
			for k,v in self.dt_types.items():
				if v ==metadata['type']:
					dt=k
					axx=list()
					axx.append(ndims)
					axx.append(dt)
					axx=axx+list(dims)
					#import numpy as np
					axx=numpy.asarray(axx,dtype='int64')
					return axx
		except Exception as e:
			print (e)
			pass

	def H5VL_python_dataset_write(self, obj_id, mem_type_id, mem_space_id, file_space_id, plist_id, buf, req):
		#print ('dataset write')
		print ("-----------------ENTER Dataset Write-----------------")
		try:
			#print ('in python dataset write, obj is ',obj_id)
			dst_parent_obj=self.obj_list[obj_id]
			#print ('in dset write, haha, dst_parent_obj:%s'%dst_parent_obj)
			z = dst_parent_obj
			dst_container_name=z[:z.find(z.split('\\')[-1])-1]
			dst_object_name=z.split('\\')[-1]
			try:
				#dst_parent_obj[:] = buf
				#call swift_object_create(container = , sciobj_name = , sciobj_source = )
				#print ('puting dst object, container=%s, objec=%s'%(dst_container_name,dst_object_name))
				metadata = swift_metadata_get(container=dst_container_name,sciobj_name=dst_object_name)
				swift_object_create(container=dst_container_name, sciobj_name=dst_object_name, sciobj_source=buf)
				#swift_metadata_get(container = dst_container_name, sciobj_name = dst_obj_name, sciobj_source = sci_obj_source)
                                sci_obj_meta={}
                                sci_obj_meta['type'] = str(metadata['type'])
                                sci_obj_meta['dims'] = str(metadata['dims'])
                                sci_obj_meta['ndim'] = str(metadata['ndim'])
                                #print ('sci obj meta:',sci_obj_meta)
                                r1=swift_metadata_create(container = dst_container_name, sciobj_name = dst_object_name, sciobj_metadata=sci_obj_meta)

				curid = self.obj_curid
				#print ("------- PYTHON H5Dwrite OK")
				print ("-----------------LEAVE Dataset Create-----------------")
				return curid
			except Exception as e:
				print ('dataset write in python failed with error: ',e)
				return -1
		except Exception as e:
			print ('retrieve obj failed in python dataset write: ',e)
			return -1

	def H5VL_python_dataset_read(self, obj_id, mem_type_id, mem_space_id, file_space_id, plist_id, buf, req):
		try:
			#print ('in python dataset read, obj is ',obj_id)
			dst_parent_obj=self.obj_list[obj_id]
			#print ('what is this:ds_parent_obj:',dst_parent_obj)
			z = dst_parent_obj.replace("/","\\")
			dst_container_name=z[:z.find(z.split('\\')[-1])-1]
                        dst_object_name=z.split('\\')[-1] 
			try:
				'''
					buf[:] = dst_parent_obj[:] # TODO: make sure memcopy free
					print ("passed in buffer has shape:,",buf.shape)
	            			print ("data to be returned has shape:,",dst_parent_obj)
		        		buf[:] = dst_parent_obj[:]
	        			Direct read from HDF5 file into numpy array
		        		print (buf)
		        		print (buf.flags)
		        	'''
				#dst_parent_obj.read_direct(buf)
				
				print ('in python dataset read, container:%s, objects:%s'%(dst_container_name,dst_object_name))
				print ('type and shape of input buf is')
				print (type(buf),buf.shape)
				x=swift_object_download(container=dst_container_name, sciobj_name=dst_object_name).reshape(buf.shape)
				#swift_object_download(container=dst_container_name, sciobj_name=dst_object_name, dst_obj=buf)
				print ('type and shape of returned buffer:',type(x),x.shape)
				#numpy.copyto(buf,x)
				print ("------- PYTHON H5Dread OK")
				#print('x is')
				#print(x)
				#print('before copy, buf is')
				#print(buf)
				#buf=buf.reshape(x.shape)
				#buf[:]=x
				#print ('length of x:%d'%(len(x)))
				#for i in range(len(x)):
				#	print ('Loop:%d'%i)
				#	buf[i]=x[i]
				#	print(buf)
				#print('after copy, buf is:\n',buf)
				return x
			except Exception as e:
				print ('dataset read in python failed with error: ',e)
		except Exception as e:
			print ('retrieve obj failed in python dataset write')
			return -1

	def H5VL_python_group_close(self, grp_id, dxpl_id, req):
		try:
			if(len(self.obj_list)==0):
				#print ("------- PYTHON H5Gclose OK")
				return 1
			grp_obj = self.obj_list[grp_id] # retrive the group handle/obj based on id 'grp_id'
			if grp_obj == None:
				print ("Python Group Obj is none")
				return 1
			else:
				del(self.obj_list[grp_id])
				#print ("------- PYTHON H5Gclose OK")
				return 1
		except Exception as e:
			print ('dataset close failed in python with error:',e)
			return -1
