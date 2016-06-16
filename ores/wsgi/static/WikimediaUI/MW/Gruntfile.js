module.exports = function(grunt) {
  require('jit-grunt')(grunt);

  grunt.initConfig({
      
    less: {
      development: {
        options: {
          compress: false,
        },
        files: {
          "mediawiki.css": "mediawiki.less"
        }
      }
    },
    cssmin: {
        css: {
            src: 'mediawiki.css',
            dest: 'mediawiki.min.css'
        }
    },
    watch: {
      styles: {
        files: ['*.less'], // which files to watch
        tasks: ['less', 'cssmin'],
        options: {
          nospawn: true
        }
      }
    }
  });

  grunt.registerTask('default', ['less', 'cssmin', 'watch']);
};