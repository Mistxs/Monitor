import re

response = '''['{"exception"=>{"message"=>"no sale state for abonement payment", "code"=>0, "class"=>"RuntimeException", "file"=>"/opt/lib/erp/server.136799.d760a37b/src/More/Loyalty/Services/LoyaltyAbonementAutoPaymentService.php:192", "trace"=>["/opt/lib/erp/server.136799.d760a37b/src/CDB.php:200", "/opt/lib/erp/server.136799.d760a37b/src/CDB.php:252", "/opt/lib/erp/server.136799.d760a37b/src/More/Loyalty/Services/LoyaltyAbonementAutoPaymentService.php:243", "/opt/lib/erp/server.136799.d760a37b/src/More/Loyalty/Commands/LoyaltyAbonementAutoPaymentProcessCommand.php:34", "/opt/lib/erp/server.136799.d760a37b/src/More/Command/AbstractDaemonCommand.php:208", "/opt/lib/erp/server.136799.d760a37b/vendor/php-amqplib/php-amqplib/PhpAmqpLib/Channel/AMQPChannel.php:1044", "/opt/lib/erp/server.136799.d760a37b/vendor/php-amqplib/php-amqplib/PhpAmqpLib/Channel/AbstractChannel.php:220", "/opt/lib/erp/server.136799.d760a37b/vendor/php-amqplib/php-amqplib/PhpAmqpLib/Channel/AbstractChannel.php:374", "/opt/lib/erp/server.136799.d760a37b/src/More/Command/AbstractDaemonCommand.php:300", "/opt/lib/erp/server.136799.d760a37b/vendor/symfony/console/Command/Command.php:298", "/opt/lib/erp/server.136799.d760a37b/src/More/Command/AbstractCommand.php:153", "/opt/lib/erp/server.136799.d760a37b/vendor/symfony/console/Application.php:1058", "/opt/lib/erp/server.136799.d760a37b/vendor/symfony/console/Application.php:301", "/opt/lib/erp/server.136799.d760a37b/vendor/symfony/console/Application.php:171", "/opt/lib/erp/server.136799.d760a37b/public/index.php:19"]}, "record_autopayment_status"=>3, "record_id"=>628766501, "record_last_update"=>"2023-05-26 16:49:59", "record_paid_full"=>0, "salon_id"=>780413, "record_attendance_status"=>0}']'''

# Ищем значение record_id с помощью регулярного выражения
record_id_match = re.search(r'"record_id"=>(\d+)', response)

if record_id_match:
    record_id = record_id_match.group(1)
    print(record_id)
else:
    print("Record ID not found")
