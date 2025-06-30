BEGIN;

CREATE TABLE IF NOT EXISTS public.posts
(
    uuid bigint NOT NULL,
    content character varying NOT NULL,
    date timestamp without time zone NOT NULL,
    PRIMARY KEY (uuid)
);

CREATE TABLE IF NOT EXISTS public.sentiment
(
    post_uuid bigint NOT NULL,
    llm_name character varying NOT NULL,
    sentiment_name character varying NOT NULL,
    sentiment_analysis character varying NOT NULL,
    PRIMARY KEY (post_uuid, sentiment_name)
);

ALTER TABLE IF EXISTS public.sentiment
    ADD FOREIGN KEY (post_uuid)
    REFERENCES public.posts (uuid) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;

END;