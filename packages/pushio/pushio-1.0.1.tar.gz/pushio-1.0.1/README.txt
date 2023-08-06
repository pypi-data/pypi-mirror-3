This module makes it simple to send push notifications via Push IO's push notification service.

In order to use this, you need to have an account with Push IO (https://manage.push.io) and have an
app setup.

It's really simple to get started. Just have your App ID and Service Secret handy and substitute
the placeholders with them when creating the API object.

	from pushio import API
	from pushio import Notification

	pushioAPI = API("Your App ID", "Your Service Secret", debug=True)

Then, create a Notification object and determine how you want to send–– test device, broadcast, or category push notifications.
	
	testNotification = Notification(message="Hello, Test World")
	pushioAPI.sendTestDevicePushNotification(testNotification)
	
	notification = Notification(message="Hello, Entire World")
	pushioAPI.sendBroadcastPushNotification(notification)

	notification = Notification(message="Hello, Sports World")
	categories = "Sports"
	pushioAPI.sendCategoryPushNotification(notification, categories)
	
	notification = Notification(message="Hello, Sports or US World")
	categories = "Sports or US"
	pushioAPI.sendCategoryPushNotification(notification, categories)


You can even do complex things like pass platform specific values, with each other platform getting the Notification object values.

	from pushio import APNS

	apns = APNS(alert="Hello, iOS World", sound="beep.wav")
	notification = Notification(message="Hello, Entire World", payload_apns=apns.payload)
	pushioAPI.sendBroadcastPushNotification(notification)

There is much more you can do. Please check out the documentation for more examples.

–– Dan Burcaw, Co-Founder Push IO

