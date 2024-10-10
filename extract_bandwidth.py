import subprocess

# Define common variables
protocols = ["tcp", "udp"]
hops = ["1", "3", "5"]
txt_suffix = ".txt"

# AWK command template
#       /sec/ - matches lines containing "sec"
#       /-/ - matches lines containing a hyphen (present in the interval timestamps)
#       !/sender|receiver/ - excludes lines containing "sender" or "receiver"
#
#       split($3, a, "-")
#           $3 refers to the third field/column in the input line (the Interval column, like "0.00-1.00")
#           a is an array where the split results will be stored
#           "-" is the delimiter used to split the string
#           So for "0.00-1.00", a[1] will contain "0.00" and a[2] will contain "1.00"
#
#       Input line:[  7]   0.00-1.00   sec   265 MBytes  2.22 Gbits/sec  191797
#           $1 = [  7]
#           $2 = 0.00-1.00
#           $3 = sec
#           $4 = 265
#           $5 = MBytes
#           $6 = 2.22
#           $7 = Gbits/sec
#           $8 = 191797
awk_command_template = "awk '/sec/ && /-/ && !/sender|receiver/ {{split($3, a, \"-\"); print a[1], $7}}' {input_file} > {output_file}"

# Iterate over protocols and hops to generate input and output file names
for protocol in protocols:
    for hop in hops:
        hop_text = f"{hop}-hop"
        input_file = f"{protocol}-{hop_text}-raw{txt_suffix}"
        output_file = f"{protocol}-{hop_text}-data{txt_suffix}"

        # Create the AWK command for the current file
        awk_command = awk_command_template.format(
            input_file=input_file, output_file=output_file)

        # Execute the command
        subprocess.run(awk_command, shell=True, check=True)

print("AWK commands executed successfully for all files.")
