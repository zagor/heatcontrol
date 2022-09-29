# heatcontrol
Control your HVAC based on your hourly electricity rate

![prices](https://user-images.githubusercontent.com/229360/192975518-708ffd28-0fb1-489e-9463-216c73f2dfd0.png)

## The concept
Heatcontrol changes the settings of your HVAC system every hour based on the
momentary price of electricity.

You can think of your house as a "heat battery". 
It constantly drains heat to the outside, so you constantly have to add heat to stay comfortable.
But you don't have to add heat at the exact same rate as the house drain it.
Thanks to _thermal inertia_, you can "charge up" the house a little extra during cheap hours
and let it drain a little extra during expensive hours. 
This results in a little more variation in indoor temperatures (both up and down) but can produce
significant cost savings if there are big swings in your hourly electricity price.

## How to use it
You configure two price limits: A high limit and a low limit.
This defines three price intervals: Low, mid and high.
For each price interval, you configure the HVAC settings to use. 

Point your browser to port 8080 for a configuration interface and to /prices for price display.

## FAQ

### What HVACs are supported?
Toshiba, Mitsubishi and Daikin air/air heat pumps are currently supported, 
using a simple gpio-driven IR transmitter.

### Can I add support for my HVAC?
Probably. If it's just another IR remote it should be fairly easy.

### A smart thermostat? Hasn't this been solved already? Nest etc.
There are many commercially available solutions to this problem.
But I'm a tweaker and optimizer, and I'm rarely happy with shrink-wrapped solutions.
I also don't like having my "smart home" functions depend on cloud services.
