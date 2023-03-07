# 14:07 07/03/2023
# This generates a custom install.cmd, with the desired IP address of caladium

def main():
    caladium_server_address = "20.166.76.162" # This is the default IP for the caladium instance

    # Read in a custom IP or press enter to use default
    if len(input_address := input(caladium_server_address + "> ")) != 0:
        caladium_server_address = input_address

    # Read in install.cmd, swap {0} for the IP above
    with open("scripts/install.cmd") as install_cmd_input_f:
        install_cmd_code = install_cmd_input_f.read().format(caladium_server_address)

        # Write install_cmd_code to install.cmd in build directory
        with open("build/caladium/install.cmd", "w") as install_cmd_output_f:
            install_cmd_output_f.write(install_cmd_code)

if __name__ == "__main__":
    main()
