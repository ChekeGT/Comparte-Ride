"""Invitations models manager."""

# Django
from django.db import models

# Utilities
import random
from string import (
    ascii_letters,
    digits,
)


class InvitationManager(models.Manager):
    """Invitation manager

    Handles CRUD of invitation model,
    """

    POOL = ascii_letters + digits
    MAX_CODE_LENGTH = 50

    def create(self, **kwargs):
        """Handles creating the invitation with an unique code."""

        code = kwargs.get('code', self.create_invitation_code())

        while self.filter(code=code).exists():
            code = self.create_invitation_code()

        kwargs['code'] = code
        return super(InvitationManager, self).create(**kwargs)

    def create_invitation_code(self):
        """Handles creating a code for invitations."""

        code = ''.join(
            random.choices(
                self.POOL,
                k=self.MAX_CODE_LENGTH
            )
        )

        return code
