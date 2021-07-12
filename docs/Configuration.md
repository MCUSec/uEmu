We detail usage of each μEmu configuration here. Ideally, you only need to configure the options in [mem_confg] for new MCUs, and use other configurations as default values.

You can also refer to the examples of configuration used in our unit-tests and  real world firmware.  More information please refer to our paper.

## [MEM_Config]

The configurations in this section is used to set memory map for bootstrapping the firmware execution. Please follows the memory map in MCU documents or memory region definition of firmware to configure the following entries.

`rom`: configure rom (code) region used for the target firmware (currently only support two separated ranges at most).

`ram`: configure ram (data) region used for the target firmware (currently only support two separated ranges at most).

`vtor`: configure the base address of vector table. Typically, the base address of vector table (vtor) should be same as the base addrees of ROM.

```
defalut usage: 
rom = <rom1_base_address>,<rom1_size>
ram = <ram1_base_address>,<ram1_size>
vtor= <rom1_base_address>
```


## [IRQ_Config]
The configurations in this section is used to control how μEmu deal with interrupts, typically is no need to adjust the default values.

`irq_tb_break`: configure the interval basic block number for external irqs invoke. Note that we use half of basic block number for dynamic analysis phase. For example, if you set 2,000 for `irq_tb_break`, μEmu will trigger one of enabled external interrupts each 2,000 basic blocks in KB extraction phase and 1,000 basic blocks in dynamic analysis phase.

`disable_irqs`: disable specific external interrupts. Typically, user should not disable any enabled external interrupts in case some firmware developers may enable unused interrupts and these interrupts are usually a empty dead loop. Since μEmu will trigger all enabled interrupts, user should disable them beforhand.

`disable_systick`: disable systick interrupt until carry out specific basic blocks set via `systick_begin_point`. This configuration is rarely used and false by default unless some firmware enable  systick before initializing the function points used in the systick interrupt. The usage of this option, please refer to the example configuration of `p2im_Robot` firmware.

```
defalut usage:
irq_tb_break = 1000
disable_systick = false
disable_irqs =
```



## [INV_Config]
 The configurations in this section is used for adjusting **invalid state detection**, typically is no need to adjust the default values.
`bb_inv1`: configure the basic block number used for infinite loop monitor. The default value is 20 in our empirical study.

`bb_inv2`: configure the basic block number used for long loop detection. The default value is 2,000 in our empirical study.

`bb_terminate`: configure the basic block number used for one round KB extraction termination. The default value is 3,0000 in our empirical study.

`kill_points`: configure the additional invalid program points (start address of the basic block). This option is to deal with the false negatives of invalid state detection and is empty by default.
`alive_points` : configure the program points (start address of the basic block) which are inactivate to any invalid states. This option to deal with the false positives of invalid state detection and is empty by default. Note that since FPs of invalid state detection will lead to all paths failed for KB extraction at same point, μEmu is able to automatically identify the all `alive points` for tested firmware without any manual intervention. Thus, you do not need to configure this option at first time. Then if you find the first round KB extraction is failed due to alive points, then you can directly add them to as `alive points` and re-configure the μEmu to re-run the KB extraction.

```
defalut usage:
bb_inv1 = 20
bb_inv2 = 2000
bb_terminate = 30000
kill_points = 
alive_points = 
```



## [TC_Config]

 The configurations in this section is used for adjusting **tiring cache strategy**, typically is no need to adjust the default values.

`t2_function_parameter_num`: configure how many function parameters used for T2 entries (default is 3, up to 4).

`t2_max_context`:configure max contexts of one T2 entry can has. If this threshold has been exceed, T2 entries will be promoted to T3. (default is 5)

`t2_caller_level`:configure the level of caller stack used for T2 entries (default is 3, up to 5).

`t3_max_symbolic_count`:  configure return T3 registers as concrete values after how many times read T3 registers (defalut is 10).  Although μEmu can alleviate path exploration by nurture, it sometime still suffers from constraint solving overhead. Fortunately , most calculation of  firmware is based on the values from data registers which is usually T3 type. Thus, if you find the μEmu become very slow, you can turn down this threshold. Considering the data registers will be used as fuzzing test cases inputs,  narrowing down the range of available T3 values will not affect the μEmu emulation capability and may only increase the round of KB extraction during fuzzing test.

```
defalut usage:
t2_function_parameter_num = 3
t2_caller_level = 3
t2_max_context = 8
t3_max_symbolic_count = 100
```



## [Fuzzer_Config]

 The configurations in this section is only used for fuzzing. You can leave whole section with blank for KB extraction phase.

`fuzz_peripherals`: configure additional data registers.

`enable_fuzz`:  configure whether enable fuzzing test during dynamic analysis phase. 

`allow_auto_mode_switch`:  configure whether enable automatically switch back and forth to KB extraction during dynamic phase.

`time_out`:  configure time out used for hang detection.

`crash_points`: configure additional crash program points in case some firmware handles the memory crashes without system fault interrupts.

`allow_new_phs`: configure whether allow μEmu switch to KB extraction phase when access new peripherals during fuzzing test. 

`fork_point_count`:  configure after reading how many test-cases μEmu will re-start at fork point. Firmware usually does not consume the reading values from data registers immediately and longer input duration of reading values should may lead to deeper paths.   Thus, we highly recommend user does not invoke fork sever too frequently. The default value is 100 in our empirical study. 

`additional_writable_ranges`: configure additional writable ranges out for ram.

```
defalut usage:
# one space between different peripheral address and comma between address and width.
fuzz_peripherals = address1,width1 address2,width2
enable_fuzz = true
allow_auto_mode_switch = true
time_out = 10
crash_points = 
allow_new_phs = true
fork_point_count = 1000
additional_writable_ranges = 0x0,0x0
```



