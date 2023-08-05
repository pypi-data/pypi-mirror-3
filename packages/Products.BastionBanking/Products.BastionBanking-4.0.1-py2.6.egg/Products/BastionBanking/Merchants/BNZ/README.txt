BNZ should supply you with an X509 certificate for your merchant, overcopy the gateway.cer file
with this.

Once you've created your BastionMerchantService, you need to set the cert_password and merchant_id
properties of your BNZ service.

At this stage, user is documentational in that it is part of the CLIENTREF sent to the bank.

If you want to test your credentials, simply edit the bnz.py bnz constructor and hard-code your 
values.  You can then type:

python bnz.py

To run the BNZ-recommended test suite, from which you should then be eligible for your 
production X509 certificate.

Please do visit http://www.last-bastion.net/BastionBanking and provide feedback for this product.
