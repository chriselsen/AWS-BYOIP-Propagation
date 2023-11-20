# AWS Bring your own IP addresses (BYOIP) propagation times 
This repository provides tools for the research of BGP propagation times for [AWS Bring-your-own-IP (BYOIP)](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-byoip.html)

**If you enjoy this work, please consider sponsoring:**

[![Buy Me A Coffee](https://raw.githubusercontent.com/chriselsen/chriselsen/main/buymeacoffee.png)](https://www.buymeacoffee.com/chriselsen)
[![Support via PayPal](https://raw.githubusercontent.com/chriselsen/chriselsen/main/paypal-donate.png)](https://www.paypal.me/christianelsen)
[![Sponsor on Github](https://raw.githubusercontent.com/chriselsen/chriselsen/main/github-sponsor.png)](https://github.com/sponsors/chriselsen)

## What is BYOIP?
With [AWS BYOIP (VPC)](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-byoip.html) you can bring part or all of your publicly routable IPv4 or IPv6 address range from your on-premises network to your AWS account. You continue to control the address range, but by default, AWS advertises it on the internet. After you bring the address range to AWS, it appears in your AWS account as an address pool.

## BGP propagation times
When announcing or withdrawing a BGP prefix, these changes are not instantly visible throughout all autonomous systems (AS) that make up the Internet. Due to various factors, there are certain delays for this propagation. In the case of AWS BYOIP, in addition to the BGP propagation delay an additional internal processing delay after calling the [AdvertiseByoipCidr](https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_AdvertiseByoipCidr.html) or [WithdrawByoipCidr](https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_WithdrawByoipCidr.html) API has to be factored in. 

The tools in this repository should allow you to determine this propagation delay - consisting of the delay due to the processing of the AWS VPC API as well as the inherent delays of BGP route updates across the global Internet. 

## How does this work
For this project the IPv6 prefix ```2602:fb2a:ff::/48``` was set aside and [configured as AWS BYOIP](https://www.edge-cloud.net/2022/07/19/hands-on-with-aws-byoip/). In addition a Lambda script triggers regular announce and withdraw actions on this particular prefix. 
More specifically this AWS BYOIP range is announced every even hour (UTC) and withdrawn every uneven hour (UTC). Therefore looking at BGP route tables at various places around the globe aound this time will provide an indication of the propagation times. 

### Backend
On the "backend" side a [Lambda Script](https://github.com/chriselsen/AWS-BYOIP-Propagation/blob/main/backend/LambdaAnnounceWithdrawBYOIP.py) is triggered via [EventBridge every hour on the hour](https://docs.aws.amazon.com/lambda/latest/dg/services-cloudwatchevents-expressions.html). 

On even hours (UTC) the event action of "advertise" triggeres the configured BYOIP CIDR to be advertised. 
On uneven hours (UTC) the event action of "withdraw" causes the CIDR to be withdrawn.
As EventBridge triggered Lambda scripts run with a slight random delay of a few seconds, the exact timestamp of the last run
can be determined here: https://byoip.as213151.net/us-east-1.html

### Frontend
You can run the "frontend" client - a [Python script](https://github.com/chriselsen/AWS-BYOIP-Propagation/blob/main/scripts/ripe-ris-byoip-client.py) that uses the [RIPE Routing Information Service Live (RIS Live) feed](https://ris-live.ripe.net/). RIS Live is a feed that offers BGP messages in real-time. It collects information from the RIS Route Collectors (RRCs) and uses a WebSocket JSON API to monitor and detect routing events around the world.

By selectively listening to BGP messages related to the IPv6 prefix ```2602:fb2a:ff::/48``` around hour marks, you can compare the timestamp of messages received by the various RIS Route Collectors (RRCs) to the timestamp from https://byoip.as213151.net/us-east-1.html on when the corresponding change at the source occured. 

As an alternative you can also look at the [RIPE Routing Information Service Live (RIS Live) feed](https://ris-live.ripe.net/) directly via a browser. 

## Examples

Below you can see the screenshot from ```https://ris-live.ripe.net/``` where an "announcement" UPDATE message was received from ASN 396998 by the RIS Route Collector [RRC11 -- NYIIX, New York City, New York, US)](https://www.ris.ripe.net/peerlist/rrc11.shtml) at the timestamp 1700510430.03. 

![](https://raw.githubusercontent.com/chriselsen/AWS-BYOIP-Propagation/main/examples/BYOIP-RIPE-RIS-Output.png)

Looking at the output of ```https://byoip.as213151.net/us-east-1.html``` around this time would provide you with:
```
aws-region: us-east-1
action: advertise
prefix: 2602:fb2a:ff::/48
asn: 213151
date: 2023-11-20 20:00:06 UTC
timestamp: 1700510406.78
```

Calculating the difference of these timestamps ( 1700510430.03 - 1700510406.78 = 23.25 ) will therefore allow you to determine that this particular ASN at NYIIX, New York City, New York, US had converged to have a path for the IPv6 prefix ```2602:fb2a:ff::/48``` at 23.25 seconds after the [AdvertiseByoipCidr](https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_AdvertiseByoipCidr.html) API was called.

If you are only interested in learning when a certain ASN - e.g. AS213151 - receives the update, stick ```^213151``` into the "path" field if that ASN [peers with RIPE RIS](https://www.ris.ripe.net/peerlist/all.shtml) or ```213151``` otherwise. 

## Analyzing data

Using the [RIPE RIS AWS BYOIP example script](https://github.com/chriselsen/AWS-BYOIP-Propagation/blob/main/scripts/ripe-ris-byoip-client.py) you can e.g. collect the above propagation time for multiple locations and ASN and create a histogram of the propagation delays. 

Below is an example, where you can see that a majority of ASN have converged at around 18.3 seconds, as well as 19.3 seconds after the [AdvertiseByoipCidr](https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_AdvertiseByoipCidr.html) API was called.

![](https://raw.githubusercontent.com/chriselsen/AWS-BYOIP-Propagation/main/examples/BYOIP-Propagation-Times.png)

## IPv4 vs IPv6
You might ask: "What about IPv4 or peers that don't support IPv6?" or "Can you also set this up with IPv4?". The short answers are: Internet peers that don't support IPv6 nowadays really need to get their act together. And between IPv4 and IPv6 the propagation times should be pretty much the same. Nevertheless, if you have a /24 public IPv4 prefix laying around that you want to donate for this project, let me know. 

## Changelog

* **2023-11-18:** Changed prefix to 2602:fb2a:ff::/48 and added support for [AWS BYOASN](https://docs.aws.amazon.com/vpc/latest/ipam/tutorials-byoasn.html) with the ASN 213151.
