# heatcontrol
Control your heating based on electricity spot price

## The concept
In most homes, you can turn off the heat for an hour or more without adverse side effects.
This is due to buildings having _thermal mass_, which provides _thermal inertia_, i.e resistance against temperature changes.

You can think of a house like a heat battery. 
It constantly leaks/drains heat to the outside, and you constantly add heat to remain comfortable.

But you don't have to add heat at the same speed as the house drain it.
Thanks to the thermal inertia, you can "charge" the house a little extra during cheap hours
and let it drain a little extra during expensive hours.

Heatcontrol downloads spot price data from your electricity company and uses that to control your heating system.

## How to use it
You configure two price limits: A high limit and a low limit. This defines three price intervals: Low, mid and high.
For each price interval, you configure the temperature setting to use. 

Point your browser to port 8080 for a configuration interface and a price visualization in /prices.

## FAQ

### What heating devices are supported?
Currently only Toshiba and Mitsubishi air/air heatpumps are supported, signalled using a custom IR transmitter.

### A smart thermostat? Hasn't this been solved before? Nest etc.
Absolutely. There are lots of commercial solutions to this problem.
But I am a tweaker and optimizer, and am rarely happy with commercial solutions.
Also, I don't like to have my home controlled by cloud-connected systems.
