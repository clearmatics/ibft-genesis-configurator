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

Example of `pod.spec` for using it in kubernetes:
```yaml
spec:
  restartPolicy: Never
  containers:
  - name: init-job02-ibft-genesis-configurator
    image: clearmatics/ibft-genesis-configurator:latest
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
