-- Update module name in ir_module_module :

DROP AGGREGATE IF EXISTS public.first(anyelement);
DROP FUNCTION public.first_agg ( anyelement, anyelement );

DROP AGGREGATE IF EXISTS public.last(anyelement);
DROP FUNCTION public.last_agg ( anyelement, anyelement );