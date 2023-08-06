%(head_prefix)s
%(head)s
%(stylesheet)s
    <script type="text/javascript"><!--
      // Add a trailing slash to the URL, if it does not end in `.html' or `/'.
      // Elegant solution from David Chambers [Atlassian]
      if (!/(\.html|\/)$/.test(location.pathname)) {
          location.pathname += '/';
      }
      //--></script>
%(body_prefix)s
%(body_pre_docinfo)s
%(docinfo)s
%(body)s
%(body_suffix)s
