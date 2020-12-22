function similitud(tit, abst, topics) {
    $('#modalbody').html("");
    $('#exampleModal').modal({ backdrop: 'static', keyboard: false })
    $('#cargando').show();
    $.ajax({
        url: `/similitud?tit=${tit}&abst=${abst}&topic=${topics}`,
        type: 'GET',
        success: function(rec) {
            let pubs = `<div class="row" id="content-pubs">
            `;
            for (let index = 0; index < rec.length; index++) {
                pubs += `
                            <div class="col-12" style="margin-top: 15px;">
                                <div class="card h-100">
                                    <div class="card-body">
                                    <img src="https://explorable.com/sites/default/files/images/APA-Title-Page-Example-1-2013.jpg" alt="" style="float: left; margin-right: 20px; width: 11%; height: 150px;">`;
                pubs += `<h3 class="card-title">${rec[index][0]}</h3>`;
                pubs += `<label> <strong>by</strong> ${rec[index][2]} <strong>Similitud:</strong> ${ rec[index][4] } </label> `;
                pubs += `<p class="card-text" style="font-size: 8pt;text-align: justify;"> ${ rec[index][1] }</p>`;
                pubs += `<label style="font-size: 8pt;">Keywords: ${ rec[index][3] } </label>`;
                pubs += `
                            </div>
                        </div>
                    </div>`;
            }
            pubs += `</div>`;
            $('#cargando').hide();
            $('#modalbody').html(pubs);

        },
        error: function(err) {
            $('#cargando').hide();
            console.log(err);
            alert(err);
        }
    });

}


function generar() {
    $('#boton').attr("disabled", true);
    $('#result').hide();
    $('#cargando1').show();
    $('#textareagenerado').val("");
    $.ajax({
        url: `/generar?texto=${$('#textareareal').val()}`,
        type: 'GET',
        success: function(rec) {
            //console.log(rec);
            $('#textareagenerado').val(rec[0]);
            $('#result').text(`Similitud Jaccard: ${rec[1]}`)
            $('#result').show();
            $('#boton').attr("disabled", false);
            $('#cargando1').hide();
        },
        timeout: 1110000,
        error: function(err) {
            $('#boton').attr("disabled", false);
            $('#cargando1').hide();
            alert(err);
            console.log(err);
        }
    });
}