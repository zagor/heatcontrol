# heatcontrol
Control your heating based on electricity spot price

## The concept
In most homes, you can turn off the heat for an hour or more without adverse side effects.
This is due to buildings having _thermal mass_, which provides _thermal inertia_,
i.e resistance against temperature changes.

You can think of a house like a heat battery. 
It constantly leaks/drains heat to the outside, and you constantly add heat to remain comfortable.

But you don't have to add heat at the same speed as the house drain it.
Thanks to the thermal inertia, you can "charge" the house a little extra during cheap hours
and let it drain a little extra during expensive hours.

Heatcontrol downloads spot price data from your electricity company and uses that to control your heating system.

## How to use it
You configure two price limits: A high limit and a low limit.
This defines three price intervals: Low, mid and high.
For each price interval, you configure the heater setting to use. 

Point your browser to port 8080 for a configuration interface and a price visualization in /prices.

## FAQ

### What heating devices are supported?
Toshiba, Mitsubishi and Daikin air/air heat pumps are currently supported, 
using a simple gpio-driven IR transmitter.

### Can I add support for my device?
Probably. If it's just another heat pump with an IR remote it should be fairly easy.

### A smart thermostat? Hasn't this been solved already? Nest etc.
There are many commercially available solutions to this problem.
But I'm a tweaker and optimizer, and I'm rarely happy with shrink-wrapped solutions.
I also don't like having my "smart home" functions depend on cloud services.
