.. _quickstart:

Rain QuickStart
===============

Requirements
------------

At this moment, our software only provides command line interfaces. Thus, users need access to the machine where the client part of the 
software is installed. Currently, this is installed and configured in the India cluster (``india.futuregrid.org``). Since our software
is going to interact with different cloud infrastructures, users need to have the appropriated credentials for each case.

* If users want to register and run images on Eucalyptus, they need an Eucalyptus account, download and uncompress the credentials (see 
  `FG Eucalyptus Tutorial <https://portal.futuregrid.org/tutorials/eucalyptus>`_). The important file is 
  the ``eucarc`` that contains the needed information about Eucalyptus and the user.
* If users want to register and run images on OpenStack, they need an OpenStack account (see 
  `FG OpenStack Tutorial <https://portal.futuregrid.org/tutorials/openstack>`_). User credentials should be in his ``HOME`` directory of the 
  India cluster. After uncompressing the credentials file, user will find the ``novarc`` file that contains important information 
  about Nimbus and the user.
* If users want to register and run images on Nimbus, they need a Nimbus account 
  (`FG Nimbus Tutorial <https://portal.futuregrid.org/tutorials/nimbus>`_). We are going to use the Nimbus infrastructure available 
  in the Hotel cluster from India (The other Nimbus deployments should work if they have the kernels needed by the images). 
  User credentials should be in his ``HOME`` directory of the Hotel cluster (``hotel.futuregrid.org``). Users have to copy and uncompress 
  their credentials in their ``HOME`` directory of India. Then, users have to create a directory called ``.nimbus`` in their ``HOME`` directory
  of India and copy the files ``usercert.pem`` and ``userkey.pem``. Other important file is the ``hotel.conf`` that contains information 
  about Nimbus and the user user.
  
Once users have the appropriate accounts, they can login on India and use the module functionality to load the environment variables:

   ::

      $ ssh <username>@india.futuregrid.org
      $ module load futuregrid

.. note::
   At this point, users have to explicitly request access to the Image Management and rain tools by sending a ticket to `https://portal.futuregrid.org/help <https://portal.futuregrid.org/help>`_.

FG-Shell vs Command Line Interfaces
-----------------------------------

To ease the use of the FG tools, we have created a shell that provides a common interface for all these tools. So, users just need to 
remember how to execute the shell. Once users login into the shell, a number of features will be exposed to them. These features include
help, command's auto-completion, and list of available commands organized by tool. Moreover, users only need to type the password 
when they login into the shell.

Users can log into the shell by executing:

   ::

      $ fg-shell -u <username>

.. note::
   Users need to use their FutureGrid portal password.

More information about using the shell can be found in the :ref:`FutureGrid Shell Manual <man-shell>`.
 

Using Image Repository
----------------------

The Image Repository is a service to query, store, and update images through a unique and common interface. Next, we show some examples of 
the Image Repository usage (``fg-repo`` command). More details can be found in the :ref:`Image Repository Manual <man-repo>`.

Additionally, the Image Repository manages the user database for all the image management components. This database is used to authorize users, to 
control the user's quotas and to record usage information. Therefore, this database complements the LDAP server which is mainly focused on the 
user authentication. 

When using ``fg-shell``, users need to load the Image Repository context by executing ``use repo`` inside the shell. The Image Repository environment 
is also included in the Image Management (``image``) and Rain (``rain``) contexts. Once there is an active context, the ``help`` command
will show only the available commands for such context. Available contexts can be listed using the ``contexts`` command. More information 
about the shell can be found in the :ref:`FutureGrid Shell Manual <man-shell>`.


* Upload an image

  * Using the CLI
  
   ::
   
      $ fg-repo -p /home/javi/image.iso "vmtype=kvm&os=Centos5&arch=i386&description=this is a test description&tag=tsttag1, tsttag2&permission=private" -u jdiaz
      $ fg-repo -p /home/javi/image.iso "ImgType=Openstack&os=Ubuntu&arch=x86_64&description=this is a test description" -u jdiaz
  
  * Using the Shell 
      
   ::

      put  /home/javi/image.iso ImgType=Openstack&os=Ubuntu&arch=x86_64&description=this is a test description
      
.. note::
   The & character is used to separate different metadata fields.

* Get an image

  * Using the CLI
  
   ::

      $ fg-repo -g 964160263274803087640112 -u jdiaz   
  
  * Using the Shell 
      
   ::

      get 964160263274803087640112


* Modify the metadata of an image

  * Using the CLI
  
   ::

      $ fg-repo -m 964160263274803087640112 "ImgType=Opennebula&os=Ubuntu10" -u jdiaz   
  
  * Using the Shell 
      
   ::

      modify 964160263274803087640112 ImgType=Opennebula&os=Ubuntu10


* Query Image Repository

  * Using the CLI
  
   ::
   
      $ fg-repo -q "* where vmType=kvm" -u jdiaz
        
  * Using the Shell 
      
   ::

      list * where vmType=kvm


* Add user to the Image Repository

  * Using the CLI
  
   ::
   
      $ fg-repo --useradd juan -u jdiaz
      $ fg-repo --usersetstatus juan active
  
  * Using the Shell 
      
   ::

      user -a juan
      user -m juan status active


Using Image Generation
----------------------

This component creates images, according to user requirements, that can be registered in FutureGrid. Since FG is a testbed that 
supports different type of infrastructures like HPC or IaaS frameworks, the images created by this tool are not aimed at any specific 
environment. Thus, it is at registration time when the images are customized to be successfully integrated into the desired infrastructure.

Next, we provide some examples of the Image Generation usage (``fg-generate`` command). More details can be found in the :ref:`Image Generation Manual <man-generate>`.


When using ``fg-shell``, users need to load the Image Management context by executing ``use image`` inside the shell. The Image Management
environment is also included in the Rain (``rain``) contexts. Once there is an active context, 
the ``help`` command will show only the available commands for such context. Available contexts can be listed using the ``contexts`` 
command. More information about the shell can be found in the :ref:`FutureGrid Shell Manual <man-shell>`.


* Generate a CentOS image

  * Using the CLI
  
   ::
   
      $ fg-generate -o centos -v 5 -a x86_64 -s wget,emacs,python26 -u jdiaz      
  
  * Using the Shell 
      
   ::

      generate -o centos -v 5 -a x86_64 -s wget,emacs,python26


* Generate an Ubuntu image

  * Using the CLI
  
   ::
   
      $ fg-generate -o ubuntu -v 10.10 -a x86_64 -s wget,openmpi-bin -u jdiaz      
  
  * Using the Shell 
      
   ::

      generate -o ubuntu -v 10.10 -a x86_64 -s wget,emacs,python26


Using Image Registration
------------------------

This tool is responsible for customizing images for specific infrastructures and registering them in such infrastructures. 
Currently, we fully support HPC (bare-metal machines), Eucalyptus, OpenStack, and Nimbus infrastructures. OpenNebula is also implemented but
we do not have this infrastructure in production yet.

Next, we provide some examples of the image registration usage (``fg-register`` command). A detailed manual can be found in 
the :ref:`Image Registration Manual <man-register>`


When using ``fg-shell``, users need to load the Image Management context by executing ``use image`` inside the shell. The Image Management
environment also loads the Image Repository context. The Image Management is also included in the Rain (``rain``) contexts. Once there is an 
active context, the ``help`` command will show only the available commands for such context. Available contexts can be listed 
using the ``contexts`` command. More information about the shell can be found in the :ref:`FutureGrid Shell Manual <man-shell>`.

.. note::

   * To register an image in the HPC infrastructure, users need to specify the name of that HPC machine that they want to use with 
     the -x/--xcat option. The rest of the needed information will be taken from the configuration file.
   
   * To register an image in Eucalyptus, OpenStack and Nimbus infrastructures, you need to provide a file with the environment variables 
     using the -v/--varfile option.

* Register an image for the HPC Infrastructure India

  * Using the CLI
  
   ::
   
      $ fg-register -r 964160263274803087640112 -x india -u jdiaz      
  
  * Using the Shell 
      
   ::

      register -r 964160263274803087640112 -x india

* Register an image for OpenStack

  * Using the CLI
  
   ::
   
      $ fg-register -r 964160263274803087640112 -s -v ~/novarc -u jdiaz      
  
  * Using the Shell 
      
   ::

      register -r 964160263274803087640112 -s -v ~/novarc


* Customize an image for Ecualyptus but do not register it (here ``-v ~/eucarc`` is not needed because we are not going to register the image
  in the infrastructure)

  * Using the CLI
  
   ::
   
      $ fg-register -r 964160263274803087640112 -e -g -u jdiaz      
  
  * Using the Shell 
      
   ::

      register -r 964160263274803087640112 -e -g


* Register an image for Nimbus

  * Using the CLI
  
   ::
   
      $ fg-register -r 964160263274803087640112 -n -v ~/hotel.conf -u jdiaz      
  
  * Using the Shell 
      
   ::

      register -r 964160263274803087640112 -n -v ~/hotel.conf

* List available kernels for the HPC infrastructure India

  * Using the CLI
  
   ::

      fg-register --listkernels -x india -u jdiaz

  * Using the Shell
  
   ::

      hpclistkernels india  

* List available kernels for OpenStack

  * Using the CLI
  
   ::

      fg-register --listkernels -s -u jdiaz  

  * Using the Shell

   ::

      cloudlistkernels -s 

Using RAIN
----------

This component allow users to dynamically register FutureGrid software environments as requirement of a job submission. 
This component will make use of the previous registration tool. Currently we only support HPC job submissions.

Next, we provide some examples of the Rain usage (``fg-rain`` command). A detailed manual can be found in the :ref:`Rain Manual <man-rain>`.

When using ``fg-shell``, users need to load the Image Management context by executing ``use rain`` inside the shell. The Rain
environment also loads the Image Repository and Image Management contexts. Once there is an active context, 
the ``help`` command will show only the available commands for such context. Available contexts can be listed using the ``contexts`` 
command. More information about the shell can be found in the :ref:`FutureGrid Shell Manual <man-shell>`.


.. note::

   * To register an image in the HPC infrastructure, users need to specify the name of that HPC machine that they want to use with 
     the -x/--xcat option. The rest of the needed information will be taken from the configuration file.
   
   * To register an image in Eucalyptus, OpenStack and Nimbus infrastructures, you need to provide a file with the environment variables 
     using the -v/--varfile option.
 

* Run a job in 4 nodes on India using an image stored in the Image Repository (This involves the registration of the image in the HPC infrastructure)

  * Using the CLI
  
   ::
   
      $ fg-rain -r 1231232141 -x india -m 4 -j myscript.sh -u jdiaz      
  
  * Using the Shell 
      
   ::

      use rain    #if your prompt is different to fg-rain>
      fg-rain> launch -r 1231232141 -x india -m 4 -j myscript.sh


* Run a job in 2 nodes on India using an image already registered in the HPC Infrastructure India

  * Using the CLI
  
   ::
   
      $ fg-rain -i centosjavi434512 -x india -m 2 -j myscript.sh -u jdiaz      
  
  * Using the Shell 
      
   ::

      use rain    #if your prompt is different to fg-rain>
      fg-rain> launch -i centosjavi434512 -x india -m 2 -j myscript.sh 


* Interactive mode. Instantiate two VMs using an image already registered on OpenStack

  * Using the CLI
  
   ::
   
      $ fg-rain -i ami-00000126 -s -v ~/novarc -m 2 -I -u jdiaz      
  
  * Using the Shell 
      
   ::

      use rain    #if your prompt is different to fg-rain>
      fg-rain> launch -i ami-00000126 -s -v ~/novarc -m 2 -I

