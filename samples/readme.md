This sample (cm3.bin) should be loaded to 0. The initial SP is `0x20000400` and the entry point is `0xa81`.

It configures a `sysTick` and then output "OK\n" to UART. If the configuration fails, it outputs "Err\n". The data register is located at `0x4000C000`.


