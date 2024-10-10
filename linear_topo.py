from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel
import argparse
import subprocess
import re


class LinearRouterTopo(Topo):
    def __init__(self, n=3):
        Topo.__init__(self)

        # Add hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')

        # Add switches (acting as routers)
        routers = []
        for i in range(n):
            router = self.addSwitch(f's{i+1}')
            routers.append(router)

        # Add links
        self.addLink(h1, routers[0])
        for i in range(len(routers) - 1):
            self.addLink(routers[i], routers[i + 1])
        self.addLink(routers[-1], h2)


def run_command(command):
    """Execute a command and return its output"""
    try:
        result = subprocess.run(command, shell=True, check=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(f"Error message: {e.stderr}")
        return None


def configure_flows(net, hops):
    """Configure flows for all switches"""
    print("\nConfiguring flows...")

    for i in range(hops):
        switch = net.get(f's{i+1}')
        switch_name = switch.name

        # Configure h1 to h2 direction
        cmd = f"ovs-ofctl add-flow {switch_name} in_port=1,actions=output:2"
        run_command(cmd)

        # Configure h2 to h1 direction
        cmd = f"ovs-ofctl add-flow {switch_name} in_port=2,actions=output:1"
        run_command(cmd)

        print(f"Configured flows for {switch_name}")


def verify_flows(net, hops):
    """Verify flows for all switches in the network"""
    print("\nVerifying network flows...")
    all_correct = True

    for i in range(hops):
        switch_name = f's{i+1}'
        flows = run_command(f"ovs-ofctl dump-flows {switch_name}")

        if not flows:
            print(f"⚠ Could not retrieve flows for {switch_name}")
            all_correct = False
            continue

        # Check for required flows
        required_flows = [
            r"in_port=1.*actions=output:2",  # h1 to h2 direction
            r"in_port=2.*actions=output:1"   # h2 to h1 direction
        ]

        missing_flows = []
        for flow in required_flows:
            if not re.search(flow, flows):
                missing_flows.append(flow)

        if missing_flows:
            print(f"⚠ Missing flows in {switch_name}:")
            for flow in missing_flows:
                print(f"  - {flow}")
            print("\nCurrent flows:")
            print(flows)
            all_correct = False
        else:
            print(f"✓ Flows correctly configured for {switch_name}")

    return all_correct


def show_network_flows(net, hops):
    """Display all current flows in the network"""
    print("\nCurrent network flows:")
    for i in range(hops):
        switch_name = f's{i+1}'
        print(f"\nFlows for {switch_name}:")
        flows = run_command(f"ovs-ofctl dump-flows {switch_name}")
        if flows:
            print(flows)


class MininetCLI(CLI):
    """Extended Mininet CLI with custom commands"""
    # The do_ prefix is required in the method definition, but you don't type it when using the command in the CLI.

    def __init__(self, net, hops):
        self.hops = hops
        super().__init__(net)

    def do_verify_flows(self, _):
        """Verify all flows in the network"""
        verify_flows(self.mn, self.hops)

    def do_show_flows(self, _):
        """Show all current flows in the network"""
        show_network_flows(self.mn, self.hops)


def createNetwork(hops=3):
    topo = LinearRouterTopo(hops)
    net = Mininet(topo=topo)
    net.start()

    # Configure the flows
    configure_flows(net, hops)

    # Verify the flows
    verification_result = verify_flows(net, hops)
    if not verification_result:
        print("\n⚠ Warning: Some flows are not correctly configured!")
    else:
        print("\n✓ All flows are correctly configured!")

    print("\nAvailable commands:")
    print("  verify_flows  - Verify all network flows")
    print("  show_flows   - Display all current flows")

    # Start CLI and wait for user to exit
    MininetCLI(net, hops)

    # Cleanup when done
    net.stop()


def parseArgs():
    parser = argparse.ArgumentParser(description='Linear topology script')
    parser.add_argument('-hop',
                        type=int,
                        required=True,
                        help='Number of hops')
    args = parser.parse_args()
    return args.hop


if __name__ == '__main__':
    setLogLevel('info')
    hopsAmount = parseArgs()
    createNetwork(hopsAmount)
