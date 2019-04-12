# ibft-genesis-configurator
It will:
- get genesis template from json file
- get validators set with `addresses`, `public_key`, `name`
- get observer set with `addresses`, `public_key`, `name`
- complete genesis data with validators list, white list, allocation
- save generated result to configMap `genesis`

# Configs

* `/autonity/genesis-template.json` - should contain valid json config as a template (without validators addresses)
* `/autonity/validators` - should contain ConfigMap as a file with validators public data
* `/autonity/observers` - should contain ConfigMap as a file with observers public data

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
      - name: genesis-template
        mountPath: /autonity
  volumes:
    - name: validators
      configMap:
        name: validators
    - name: observers
      configMap:
        name: observers
    - name: genesis-template
      configMap:
        name: genesis-template
        items:
          - key: genesis.json
            path: genesis-template.json
```
