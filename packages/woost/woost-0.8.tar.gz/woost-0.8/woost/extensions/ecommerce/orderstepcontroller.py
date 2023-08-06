#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import cherrypy
from cocktail.controllers import (
    request_property,
    Form
)
from woost.controllers.notifications import pop_user_notifications
from woost.extensions.ecommerce.catalogcontroller \
    import catalog_current_state_uri


class OrderStepForm(Form):

    @request_property
    def order_steps(self):
        from woost.extensions.ecommerce import ECommerceExtension
        return ECommerceExtension.instance.order_steps

    @request_property
    def current_step(self):
        return self.controller.context["publishable"]

    @request_property
    def next_step(self):
        steps = self.order_steps
        pos = steps.index(self.current_step)
        if pos + 1 < len(steps):
            return steps[pos + 1]

    @request_property
    def previous_step(self):
        steps = self.order_steps
        pos = steps.index(self.current_step)
        if pos > 0:
            return steps[pos - 1]

    def proceed(self):
        pop_user_notifications()
        next_step = self.next_step
        if next_step is not None:
            raise cherrypy.HTTPRedirect(next_step.get_uri())

    def back(self):
        pop_user_notifications()
        previous_step = self.previous_step
        if previous_step is None:
            raise cherrypy.HTTPRedirect(catalog_current_state_uri())
        else:
            raise cherrypy.HTTPRedirect(previous_step.get_uri())


class ProceedForm(OrderStepForm):

    actions = "proceed",

    def submit(self):
        self.proceed()
        

class BackForm(OrderStepForm):

    actions = "back",

    def submit(self):
        self.back()

