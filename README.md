# Remaining MAK Tool

## Description

Microsoft has made the Volume Activation Management Tool to check license usage. For MAK (Multiple Activation Keys) you can view how many activations are remaining. Since we didn't want to start the tool every morning, I started debugging the application and made this thingy.

## Installation

This tool requires python3, lxml and requests to function.

## Usage

Standalone tool:
```$ python3 mak.py product_key_id```

Nagios check:
```$ python3 check_mak.py product_key_id warning_limit critical_limit```

## Nagios command example

```
define command {
    command_name    check-mak-remaining
    command_line    /usr/local/lib/nagios/plugins/check_mak.py $ARG1$ $ARG2$ $ARG3$
}
```