# NetHopAnalyzer

## How to use

### create a network topology with hops between 2 nodes

```bash
sudo python3 linear_topo.py -hop <hop amount>
```

### error handling

#### script stucks while creating network topology

solution: restart Open vSwitch

```bash
sudo systemctl restart openvswitch-switch
```
