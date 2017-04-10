# PeerPace

<code>PeerPace</code> is a simple webapp that gauges programmer productivity with reference
to github repos.  <code>PeerPace</code> estimates productivity by incorporating two time-varying,
loosely coupled variables:  the number of code-commits and the number of line-changes.
As well, <code>PeerPace</code> is parameterized in two key ways:

1. It lets you overweight code-commits versus line-changes, or vice-versa.
1. It allows you to control the sensitivity of performance according to the timeliness of changes -- giving variable emphasis to recent activity over historical activity.

## Licensing.

I have decided to publish this package under the MIT license.  I respectfully request that if you...