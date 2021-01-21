/*!
 * gulp
 * $ No need to npm install bar foo. Just need npm install (package.json have dependencies)
 */

// Load plugins
var gulp = require('gulp'),
    sass = require('gulp-sass'),
    bower = require('gulp-bower'),
    watch = require('gulp-watch'),
	  del = require('del');

gulp.task('powermarket_clean_styles', function() {
    return del([
        'powermarket/static/css',
        'apps/landing/static/css',
        'apps/manager/static/css',
        'apps/solar/static/css',
        'apps/supplier/static/css',
        'apps/support/static/css',
        'apps/user/static/css'
    ]);
});

gulp.task('powermarket_styles', function () {
    return gulp.src("powermarket/static/scss/*.scss")
    .pipe(sass({outputStyle: 'compressed'}))
    .pipe(gulp.dest("powermarket/static/css"))
});

gulp.task('landing_styles', function () {
    return gulp.src("apps/landing/static/scss/*.scss")
    .pipe(sass({outputStyle: 'compressed'}))
    .pipe(gulp.dest("apps/landing/static/css"))
});

gulp.task('manager_styles', function () {
    return gulp.src("apps/manager/static/scss/*.scss")
    .pipe(sass({outputStyle: 'compressed'}))
    .pipe(gulp.dest("apps/manager/static/css"))
});

gulp.task('solar_styles', function () {
    return gulp.src("apps/solar/static/scss/*.scss")
    .pipe(sass({outputStyle: 'compressed'}))
    .pipe(gulp.dest("apps/solar/static/css"))
});

gulp.task('supplier_styles', function () {
    return gulp.src("apps/supplier/static/scss/*.scss")
    .pipe(sass({outputStyle: 'compressed'}))
    .pipe(gulp.dest("apps/supplier/static/css"))
});

gulp.task('support_styles', function () {
    return gulp.src("apps/support/static/scss/*.scss")
    .pipe(sass({outputStyle: 'compressed'}))
    .pipe(gulp.dest("apps/support/static/css"))
});

gulp.task('user_styles', function() {
    return gulp.src("apps/user/static/scss/*.scss")
    .pipe(sass({outputStyle: 'compressed'}))
    .pipe(gulp.dest("apps/user/static/css"))
});

// Default tasks.
gulp.task('default', ['powermarket_clean_styles'], function() {
    gulp.start(
        'powermarket_styles',
        'landing_styles',
        'manager_styles',
        'solar_styles',
        'supplier_styles',
        'support_styles',
        'user_styles'
    );
});
