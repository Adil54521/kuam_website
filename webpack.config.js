const path = require('path');

module.exports = {
    entry: './node_modules/@ckeditor/ckeditor5-build-classic/build/ckeditor.js', // путь к билд-файлу
    output: {
        path: path.resolve(__dirname, 'static/ckeditor5/'), // куда положить итоговый файл
        filename: 'ckeditor.js', // итоговый файл
    },
    mode: 'production',
};
