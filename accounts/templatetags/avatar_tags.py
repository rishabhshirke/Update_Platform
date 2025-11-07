from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def avatar_html(user, size='md'):
    """
    Generate avatar HTML for a user.
    Returns either an image tag (if profile photo exists) or initials avatar.

    Usage: {{ user|avatar_html:"md" }}
    Sizes: sm (32px), md (64px), lg (128px)
    """
    size_map = {
        'sm': '32',
        'md': '64',
        'lg': '128',
        'xl': '200',
    }

    px_size = size_map.get(size, '64')

    if user.profile_photo:
        # Return image tag
        return mark_safe(
            f'<img src="{user.profile_photo.url}" '
            f'alt="{user.get_full_name()}" '
            f'class="avatar-circle avatar-{size}" '
            f'width="{px_size}" height="{px_size}" '
            f'style="width: {px_size}px; height: {px_size}px; object-fit: cover; border-radius: 50%;">'
        )
    else:
        # Return initials avatar
        initials = user.get_initials()
        color = user.get_avatar_color()
        font_size = int(int(px_size) * 0.4)  # 40% of avatar size

        return mark_safe(
            f'<div class="avatar-initials avatar-{size}" '
            f'style="width: {px_size}px; height: {px_size}px; '
            f'background-color: {color}; color: white; '
            f'border-radius: 50%; display: inline-flex; '
            f'align-items: center; justify-content: center; '
            f'font-weight: bold; font-size: {font_size}px; '
            f'text-transform: uppercase;">'
            f'{initials}'
            f'</div>'
        )


@register.simple_tag
def avatar_url(user):
    """Returns the URL of user's profile photo or empty string."""
    if user.profile_photo:
        return user.profile_photo.url
    return ''


@register.simple_tag
def user_initials(user):
    """Returns user's initials."""
    return user.get_initials()


@register.simple_tag
def user_avatar_color(user):
    """Returns user's avatar color."""
    return user.get_avatar_color()
