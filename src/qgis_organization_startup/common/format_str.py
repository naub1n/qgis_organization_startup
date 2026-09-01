def format_str(value: str | None, env: str | None, zone: str | None) -> str | None:
    """
    Permet de formater une variable en remplaçant les éléments $ENV$, $ZONE$ et $ZONE_MAJ$ avec la zone et l'environnement indiqués

    :param value: Texte contenant les variables à remplacer
    :param env: Nom ou siffixe de l'environnement
    :param zone: Nom de la zone
    :return:
    """
    new_value = value

    if new_value:
        if not env is None:
            new_value = new_value.replace('$ENV$', env)

        if not zone is None:
            new_value = new_value.replace('$ZONE$', zone)
            new_value = new_value.replace('$ZONE_MAJ$', zone.upper())

    return new_value