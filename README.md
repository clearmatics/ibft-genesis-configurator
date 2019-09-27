# ibft-genesis-configurator
It will:
- get genesis template from json file
- get validators set with `addresses`, `public_key`, `name`
- get observer set with `addresses`, `public_key`, `name`
- get operator-governance set with `addresses`, `public_key`, `name == 0`
- get operator-treasury set with `addresses`, `public_key`, `name == 0`
- complete genesis data with validators list, white list, allocation
- save generated result to configMap `genesis`

# Configs

* `/autonity/genesis-template.json` - should contain valid json config as a template (without validators addresses)
* `/autonity/validators` - should contain ConfigMap as a file with validators public data
* `/autonity/observers` - should contain ConfigMap as a file with observers public data
* `/autonity/operator-governance` - should contain ConfigMap as a file with operator-governance public data
* `/autonity/operator-treasury` - should contain ConfigMap as a file with operator-treasury public data


Set ips as env vars
```shell script
    validatorIps = environ.get('VALIDATOR_IPS')
    observerIps = environ.get('OBSERVER_IPS')
```

Example of `pod.spec` for using it in kubernetes:
```yaml
spec:
  restartPolicy: Never
  containers:
  - name: init-job02-ibft-genesis-configurator
    image: clearmatics/ibft-genesis-configurator:latest
    env:

    - name: VALIDATOR_IPS
      value: "{{ range $i, $e := until (atoi (printf "%d" (int64 .Values.validators.num))) }}{{index $validatorAddress $i }} {{ end }}" 

    - name: OBSERVER_IPS
      value: "{{ range $i, $e := until (atoi (printf "%d" (int64 .Values.observers.num))) }}{{index $observerAddress $i }} {{ end }}"

    volumeMounts:
      - name: validators
        mountPath: /autonity/validators
      - name: observers
        mountPath: /autonity/observers
      - name: operator-governance
        mountPath: /autonity/operator-governance
      - name: operator-treasury
        mountPath: /autonity/operator-treasury
      - name: genesis-template
        mountPath: /autonity
  volumes:
    - name: validators
      configMap:
        name: validators
    - name: observers
      configMap:
        name: observers
    - name: operator-governance
      configMap:
        name: operator-governance
    - name: operator-treasury
      configMap:
        name: operator-treasury
    - name: genesis-template
      configMap:
        name: genesis-template
        items:
          - key: genesis.json
            path: genesis-template.json
```
cmd-options:
```shell script
usage: genesis-configurator.py [-h] [-k {pod,remote}] [-legacy-genesis]
                               [--stake STAKE] [--mingasprice MINGASPRICE]
                               [--gaslimit GASLIMIT] [--balance BALANCE]

Generate genesis.json and write it to configmap

optional arguments:
  -h, --help            show this help message and exit
  -k {pod,remote}       Type of connection to kube-apiserver: pod or remote
                        (default: pod)
  -legacy-genesis       Legacy genesis.json structure (for autonity < v0.2.0)
  --stake STAKE         Stake for each validator (default: 500000)
  --mingasprice MINGASPRICE
                        Minimum Gas Price (default: 10000000000000)
  --gaslimit GASLIMIT   Gas Limit (default: 0x5F5E100)
  --balance BALANCE     Balance for each treasury operator (default: 0x2000000
                        000000000000000000000000000000000000000000000000000000
                        00)

```