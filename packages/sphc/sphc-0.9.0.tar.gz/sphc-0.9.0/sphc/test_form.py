#
#Prefer building forms using sphc.more.Form whenever possible.
#If you need to use fieldsets refer below code
#
#================================
import sphc.more

form = sphc.more.Form()

about = form.add(sphc.more.Fieldset())
about.add(sphc.tf.LEGEND('About'))
about.add_field('Name', sphc.tf.INPUT(name='name', type='text'))

contact = sphc.more.Fieldset()
contact.add(sphc.tf.LEGEND('About'))
contact.add_field('Name', sphc.tf.INPUT(name='name', type='text'))

form.add(about)
form.add(contact)
#form.add_buttons(...)

print(form.build())
#================================
#
#If there are multiple fieldsets in a page but all in different forms. Use multiple forms with fieldset embedded.
#
#Existing sphc.more.Form has no chnages.
#Don't forget to Update sphc
