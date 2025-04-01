package com.example.aplicaciongestionequipos;

import android.os.Bundle;
import android.view.View;
import androidx.appcompat.app.AppCompatActivity;
import com.google.android.material.button.MaterialButton;
import com.google.android.material.snackbar.Snackbar;
import com.google.android.material.textfield.TextInputEditText;
import com.google.firebase.firestore.CollectionReference;
import com.google.firebase.firestore.DocumentSnapshot;
import com.google.firebase.firestore.FirebaseFirestore;

import java.util.HashMap;
import java.util.Map;

public class CrearPartidoActivity extends AppCompatActivity {

    private TextInputEditText equipoLocalEditText, equipoVisitanteEditText, fechaEditText, horaEditText;
    private MaterialButton crearPartidoButton;
    private FirebaseFirestore db;
    private CollectionReference calendarioRef;
    private View rootView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_crear_partido);

        rootView = findViewById(android.R.id.content);
        equipoLocalEditText = findViewById(R.id.equipoLocalEditText);
        equipoVisitanteEditText = findViewById(R.id.equipoVisitanteEditText);
        fechaEditText = findViewById(R.id.fechaEditText);
        horaEditText = findViewById(R.id.horaEditText);
        crearPartidoButton = findViewById(R.id.crearPartidoButton);

        db = FirebaseFirestore.getInstance();
        calendarioRef = db.collection("Calendario");

        crearPartidoButton.setOnClickListener(v -> crearPartido());
    }

    private void crearPartido() {
        String local = equipoLocalEditText.getText().toString().trim();
        String visitante = equipoVisitanteEditText.getText().toString().trim();
        String fecha = fechaEditText.getText().toString().trim();
        String hora = horaEditText.getText().toString().trim();

        if (local.isEmpty() || visitante.isEmpty() || fecha.isEmpty() || hora.isEmpty()) {
            Snackbar.make(rootView, "Completa todos los campos", Snackbar.LENGTH_SHORT).show();
            return;
        }

        calendarioRef.get().addOnSuccessListener(querySnapshot -> {
            int maxId = 0;
            for (DocumentSnapshot doc : querySnapshot) {
                String id = doc.getId();
                if (id.startsWith("Partido")) {
                    try {
                        int num = Integer.parseInt(id.substring(7));
                        if (num > maxId) maxId = num;
                    } catch (NumberFormatException ignored) {}
                }
            }

            String nuevoId = String.format("Partido%03d", maxId + 1); // Partido001, Partido002...

            Map<String, Object> partido = new HashMap<>();
            partido.put("equipo_local", local);
            partido.put("equipo_visitante", visitante);
            partido.put("fecha", fecha);
            partido.put("hora", hora);
            partido.put("estado", "Pendiente");
            partido.put("goles_local", 0);
            partido.put("goles_visitante", 0);

            calendarioRef.document(nuevoId).set(partido)
                    .addOnSuccessListener(aVoid ->
                            Snackbar.make(rootView, "Partido guardado: " + nuevoId, Snackbar.LENGTH_SHORT).show())
                    .addOnFailureListener(e ->
                            Snackbar.make(rootView, "Error al guardar partido", Snackbar.LENGTH_SHORT).show());

        }).addOnFailureListener(e ->
                Snackbar.make(rootView, "Error al generar ID del partido", Snackbar.LENGTH_SHORT).show());
    }
}
