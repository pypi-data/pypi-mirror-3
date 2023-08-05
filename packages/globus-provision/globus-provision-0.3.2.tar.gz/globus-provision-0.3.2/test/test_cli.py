from globus.provision.cli import *

#args = []    
#c = demogrid_prepare(args)

#args = ["-n", "a-server"]
#c = demogrid_clone_image(args)

#args = ["--ami", "ami-480df921", 
#        "--keypair", "demogrid", 
#        "--keypair-file", "/home/borja/.ec2/demogrid.pem"]
#c = demogrid_ec2_create_chef_volume(args)

args = ["--ami", "ami-480df921", 
        #"--snapshot", "snap-132adf7e",
        "--name", "DemoGrid Base AMI w Chef files)",
        "--keypair", "demogrid", 
        "--keypair-file", "/home/borja/.ec2/demogrid.pem"]
c = demogrid_ec2_create_ami(args)

#args = []    
#c = demogrid_ec2_launch(args)

c.run()