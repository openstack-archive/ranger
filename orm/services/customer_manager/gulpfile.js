var gulp = require('gulp');
var nodemon = require('gulp-nodemon');
var shell = require('gulp-shell');
var minimist = require('minimist');
var env = require('gulp-env');

var defaultOptions = {
  string: 'env',
  default: { env: 'dev' }
};
var options = minimist(process.argv.slice(2), defaultOptions);

gulp.task('default', ['run-mock', 'run-pecan']);

gulp.task('run-pecan', shell.task(['export CMS_ENV=' + options.env + '; pecan serve config.py --reload']));
gulp.task('run-mock', function(){
	nodemon({
    script: 'rds_mock/bin/www',
    env: {'NODE_ENV': 'development'}
  });
});