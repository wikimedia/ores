source("loader/enwiki_feature_reverts.R")

feature_reverts = load_enwiki_feature_reverts(reload=T)

ggplot(
    feature_reverts,
    aes(x=added_badwords_ratio+1,
        fill=reverted,
        color=reverted,
        group=reverted
    )
) +
geom_density(
    aes(y=..density..),
    alpha=0.2
) +
scale_x_log10()

ggplot(
    feature_reverts,
    aes(x=added_misspellings_ratio+1,
        fill=reverted,
        color=reverted,
        group=reverted
    )
) +
geom_density(
    aes(y=..density..),
    alpha=0.2,
    adjust=3
) +
scale_x_log10(breaks=c(1,1.1,1.2,1.3,1.4,1.5,2,3,4,5))

ggplot(
    feature_reverts,
    aes(x=proportion_of_markup_added+1,
        fill=reverted,
        color=reverted,
        group=reverted
    )
) +
geom_density(
    aes(y=..density..),
    alpha=0.2,
    adjust=3
) +
scale_x_log10(breaks=c(1,1.5,2,3,4,5))

ggplot(
    feature_reverts,
    aes(x=proportion_of_numeric_added+1,
        fill=reverted,
        color=reverted,
        group=reverted
    )
) +
geom_density(
    aes(y=..density..),
    alpha=0.2,
    adjust=3
) +
scale_x_log10(breaks=c(1,1.1,1.2,1.3,1.4,1.5,1.6,1.7))

ggplot(
    feature_reverts,
    aes(x=proportion_of_symbolic_added+1,
        fill=reverted,
        color=reverted,
        group=reverted
    )
) +
geom_density(
    aes(y=..density..),
    alpha=0.2,
    adjust=3
) +
scale_x_log10(breaks=c(1,1.1,1.2,1.3,1.4,1.5,1.6,1.7))

ggplot(
    feature_reverts,
    aes(x=proportion_of_uppercase_added+1,
        fill=reverted,
        color=reverted,
        group=reverted
    )
) +
geom_density(
    aes(y=..density..),
    alpha=0.2,
    adjust=3
) +
scale_x_log10(breaks=c(1,1.1,1.2,1.3,1.4,1.5,1.6,1.7))

ggplot(
    feature_reverts,
    aes(x=proportion_of_uppercase_added+1,
        fill=reverted,
        color=reverted,
        group=reverted
    )
) +
geom_density(
    aes(y=..density..),
    alpha=0.2,
    adjust=3
) +
scale_x_log10(breaks=c(1,1.1,1.2,1.3,1.4,1.5,1.6,1.7))

feature_reverts$dayname_of_week_in_utc = convert.factor(
    feature_reverts$day_of_week_in_utc,
    list("0"="Sunday", "1"="Monday", "2"="Tuesday", "3"="Wednesday",
         "4"="Thursday", "5"="Friday", "6"="Saturday")
)
ggplot(
    feature_reverts,
    aes(
        x=dayname_of_week_in_utc,
        fill=reverted,
        group=reverted
    )
) +
geom_bar(
    aes(y=..density..),
    position="dodge"
)


ggplot(
    feature_reverts,
    aes(
        x=factor(hour_of_day_in_utc),
        fill=reverted,
        color=reverted,
        group=reverted
    )
) +
geom_density(
    aes(y=..density..),
    alpha=0.2
)



ggplot(
    feature_reverts,
    aes(
        x=factor(hour_of_day_in_utc),
        fill=reverted,
        group=reverted
    )
) +
geom_density(
    aes(y=..density..),
    position="dodge"
)

ggplot(
    feature_reverts,
    aes(
        x=is_custom_comment,
        fill=reverted,
        group=reverted
    )
) +
geom_bar(
    aes(y=..density..),
    position="dodge"
)

ggplot(
    feature_reverts,
    aes(
        x=is_section_comment,
        fill=reverted,
        group=reverted
    )
) +
geom_bar(
    aes(y=..density..),
    position="dodge"
)

ggplot(
    feature_reverts,
    aes(
        x=is_mainspace,
        fill=reverted,
        group=reverted
    )
) +
geom_bar(
    aes(y=..density..),
    position="dodge"
)

ggplot(
    feature_reverts,
    aes(
        x=user_is_anon,
        fill=reverted,
        group=reverted
    )
) +
geom_bar(
    aes(y=..density..),
    position="dodge"
)

ggplot(
    feature_reverts,
    aes(
        x=user_is_bot,
        fill=reverted,
        group=reverted
    )
) +
geom_bar(
    aes(y=..density..),
    position="dodge"
)

ggplot(
    feature_reverts,
    aes(
        x=longest_repeated_char_added,
        fill=reverted,
        group=reverted
    )
) +
geom_density(
    aes(y=..density..),
    position="dodge"
) +
scale_x_log10()

ggplot(
    feature_reverts,
    aes(
        x=longest_repeated_char_added+1,
        fill=reverted,
        color=reverted,
        group=reverted
    )
) +
geom_density(
    adjust=3,
    alpha=0.2
) +
scale_x_log10()

ggplot(
    feature_reverts,
    aes(
        x=longest_token_added+1,
        fill=reverted,
        color=reverted,
        group=reverted
    )
) +
geom_density(
    adjust=3,
    alpha=0.2
) +
scale_x_log10()

ggplot(
    feature_reverts,
    aes(
        x=numeric_chars_added+1,
        fill=reverted,
        color=reverted,
        group=reverted
    )
) +
geom_density(
    adjust=3,
    alpha=0.2
) +
scale_x_log10()


ggplot(
    feature_reverts,
    aes(
        x=prev_words+1,
        fill=reverted,
        color=reverted,
        group=reverted
    )
) +
geom_density(
    adjust=3,
    alpha=0.2
) +
scale_x_log10()

ggplot(
    feature_reverts,
    aes(
        x=prev_words+1,
        fill=reverted,
        color=reverted,
        group=reverted
    )
) +
geom_density(
    adjust=3,
    alpha=0.2
) +
scale_x_log10()

ggplot(
    feature_reverts,
    aes(
        x=seconds_since_last_page_edit+1,
        fill=reverted,
        color=reverted,
        group=reverted
    )
) +
geom_density(
    adjust=3,
    alpha=0.2
) +
scale_x_log10()


ggplot(
    feature_reverts,
    aes(
        x=segments_added+1,
        fill=reverted,
        color=reverted,
        group=reverted
    )
) +
geom_density(
    adjust=3,
    alpha=0.2
) +
scale_x_log10()


ggplot(
    feature_reverts,
    aes(
        x=segments_removed+1,
        fill=reverted,
        color=reverted,
        group=reverted
    )
) +
geom_density(
    adjust=3,
    alpha=0.2
) +
scale_x_log10()


ggplot(
    feature_reverts,
    aes(
        x=user_age_in_seconds+1,
        fill=reverted,
        color=reverted,
        group=reverted
    )
) +
geom_density(
    adjust=3,
    alpha=0.2
) +
scale_x_log10()
