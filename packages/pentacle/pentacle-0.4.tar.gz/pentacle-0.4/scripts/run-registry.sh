# Start up a single instance for easier debugging.
# This also lets us examine what a service process looks like to management.
# Note how the name is specified explicitly: this is because, even though it's part of the configuration,
#    it's in a section that isn't necessary recognized by the partnered application.  This is because the
#    configuration file is shared to simplify management, but the partner information that is important to
#    the manager (like the name), is only read by the manager.

export PENTACLE_CONFIG='/cygdrive/h/My Projects/Pentacle/scripts/partners/registry.ptr'
export PENTACLE_PARTNER_NAME='penobscotrobotics.us/Pentacle/SystemRegistry'
export PENTACLE_PARTNER_AUTH='[\xbc\x163\xa9\x11-A\r\xdb\x81\xcf0x\n\xca\xee\x95\xe0^\xf5f\xf7\xa0\x11B[p\x08)\xaf\xbb'
python -m pentacle.bus.partners.main
