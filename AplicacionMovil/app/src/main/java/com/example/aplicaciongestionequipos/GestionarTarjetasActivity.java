package com.example.aplicaciongestionequipos;

import android.os.Bundle;
import android.view.View;
import androidx.appcompat.app.AppCompatActivity;
import com.google.android.material.button.MaterialButton;
import com.google.android.material.snackbar.Snackbar;
import com.google.android.material.textfield.TextInputEditText;
import com.google.firebase.firestore.FirebaseFirestore;
import com.google.firebase.firestore.QueryDocumentSnapshot;

public class GestionarTarjetasActivity extends AppCompatActivity {

    private TextInputEditText inputNombreJugador, inputAmarillas, inputRojas;
    private MaterialButton btnBuscarJugador, btnGuardarTarjetas;
    private FirebaseFirestore db;
    private View rootView;
    private String jugadorIdEncontrado = null;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_gestionar_tarjetas);

        rootView = findViewById(android.R.id.content);
        db = FirebaseFirestore.getInstance();

        inputNombreJugador = findViewById(R.id.inputNombreJugador);
        inputAmarillas = findViewById(R.id.inputAmarillas);
        inputRojas = findViewById(R.id.inputRojas);
        btnBuscarJugador = findViewById(R.id.btnBuscarJugador);
        btnGuardarTarjetas = findViewById(R.id.btnGuardarTarjetas);

        btnBuscarJugador.setOnClickListener(v -> buscarJugador());
        btnGuardarTarjetas.setOnClickListener(v -> guardarCambiosTarjetas());
    }

    private void buscarJugador() {
        String nombreBuscado = inputNombreJugador.getText().toString().trim();

        if (nombreBuscado.isEmpty()) {
            mostrarSnackbar("Escribe un nombre para buscar");
            return;
        }

        db.collection("Jugadores")
                .whereEqualTo("nombre", nombreBuscado)
                .get()
                .addOnSuccessListener(query -> {
                    if (query.isEmpty()) {
                        mostrarSnackbar("Jugador no encontrado");
                        jugadorIdEncontrado = null;
                        return;
                    }

                    for (QueryDocumentSnapshot doc : query) {
                        jugadorIdEncontrado = doc.getId();

                        String amarillas = doc.getString("tarjetas_amarillas");
                        String rojas = doc.getString("tarjetas_rojas");

                        inputAmarillas.setText(amarillas != null ? amarillas : "0");
                        inputRojas.setText(rojas != null ? rojas : "0");

                        mostrarSnackbar("Jugador encontrado y cargado");
                        break;
                    }
                })
                .addOnFailureListener(e -> mostrarSnackbar("Error: " + e.getMessage()));
    }

    private void guardarCambiosTarjetas() {
        if (jugadorIdEncontrado == null) {
            mostrarSnackbar("Primero busca un jugador");
            return;
        }

        String amarillas = inputAmarillas.getText().toString().trim();
        String rojas = inputRojas.getText().toString().trim();

        db.collection("Jugadores").document(jugadorIdEncontrado)
                .update(
                        "tarjetas_amarillas", amarillas,
                        "tarjetas_rojas", rojas
                )
                .addOnSuccessListener(unused -> mostrarSnackbar("Cambios guardados correctamente"))
                .addOnFailureListener(e -> mostrarSnackbar("Error al guardar cambios"));
    }

    private void mostrarSnackbar(String mensaje) {
        Snackbar.make(rootView, mensaje, Snackbar.LENGTH_SHORT).show();
    }
}
