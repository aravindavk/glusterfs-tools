glusterfs-tools
===============

A wrapper around glusterfs cli to view/filter volume information. 

Create a shellscript in /usr/local/bin directory(make sure /usr/local/bin is in your PATH)

File name: /usr/local/bin/gfvolumes

    #!/bin/bash
    python <path to gftools>/volumes.py "$@"
    
In my system

    #!/bin/bash
    python /home/aravinda/sandbox/glusterfs-tools/gftools/volumes.py "$@"
    
Make gfvolumes executable

    chmod +x /usr/local/bin/gfvolumes
    
Now we can run gfvolumes to get the list of gluster volumes available. 

Check my [blog](http://aravindavk.in/blog/glusterfs-tools) for more details. 
